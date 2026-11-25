"""Make the figures for the Parquet and GeoParquet lesson.

Run with the course environment, giving the path to this file:

    python book/chapters/lesson-19-parquet/_make-figures.py

The figures are saved as PNG files in book/images/lesson-19/.
Everything is drawn with matplotlib, so the figures can be edited here.
"""

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# --------------------------------------------------------------------
# Setup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'images', 'lesson-19')

U = 10      # drawing units per inch
DPI = 200

# Text and neutral colors
INK = '#191919'
DARK = '#444444'
MUTED = '#666666'
FADED = '#8f8f8f'
LINE = '#b3b3b3'
SOFT = '#f4f4f4'
SKIP = '#ededed'
WHITE = '#ffffff'

# One color per column of the example table
BLUE = '#257de0'
ORANGE = '#f47230'
AQUA = '#00b894'
YELLOW = '#f2a600'
COLORS = [BLUE, ORANGE, AQUA, YELLOW]

SANS = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'

# Example table: three rows of the clean spills data
NAMES = ['spill_number', 'county', 'spill_date', 'material_family']
TYPES = ['string', 'string', 'datetime', 'string']
ROWS = [['0107132', 'Westchester', '2001-10-10', 'Other'],
        ['0405586', 'Queens', '2004-08-21', 'Other'],
        ['0204667', 'Bronx', '2002-08-02', 'Petroleum']]


# --------------------------------------------------------------------
# Drawing helpers

def tint(color, amount=0.80):
    """Mix a hex color with white. amount=0 is the color, amount=1 is white."""
    r, g, b = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    r, g, b = [round(c + (255 - c) * amount) for c in (r, g, b)]
    return f'#{r:02x}{g:02x}{b:02x}'


def new_figure(width, height):
    """Create a figure of width x height drawing units with a single empty axis."""
    fig = plt.figure(figsize=(width / U, height / U), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis('off')
    return fig, ax


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name), dpi=DPI, facecolor=WHITE)
    plt.close(fig)
    print('Saved', name)


def text_width(ax, s, size, family=SANS, weight='normal'):
    """Width of a string in drawing units."""
    t = ax.text(0, 0, s, fontsize=size, family=family, weight=weight)
    extent = t.get_window_extent(renderer=ax.figure.canvas.get_renderer())
    t.remove()
    return extent.width / ax.figure.dpi * U


def box(ax, x, y, w, h, fill=WHITE, edge=LINE, lw=1.0, ls='-', radius=0.6, z=2):
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle=f'round,pad=0,rounding_size={radius}',
                           facecolor=fill, edgecolor=edge, linewidth=lw,
                           linestyle=ls, zorder=z)
    ax.add_patch(patch)
    return patch


def label(ax, x, y, s, size=9, color=INK, ha='center', va='center',
          weight='normal', family=SANS, z=5, linespacing=1.25):
    return ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va,
                   weight=weight, family=family, zorder=z,
                   linespacing=linespacing)


def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=1.4):
    patch = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                            mutation_scale=11, color=color, linewidth=lw,
                            shrinkA=0, shrinkB=0, zorder=4)
    ax.add_patch(patch)
    return patch


def step(ax, x, y, n, radius=1.4):
    """Draw a numbered circle."""
    circle = plt.Circle((x, y), radius, facecolor=INK, edgecolor=INK, zorder=6)
    ax.add_patch(circle)
    label(ax, x, y - 0.05, str(n), size=8, color=WHITE, weight='bold', z=7)


def cell(ax, x, y, s, color, w=None, h=3.4, size=8, pad=0.75, family=MONO,
         weight='normal', skipped=False, strong=False):
    """Draw a value inside a tinted box. Returns the width of the box.

    If w is None the box is as wide as the text plus the padding.
    """
    if w is None:
        w = text_width(ax, s, size, family, weight) + 2 * pad
    if skipped:
        box(ax, x, y, w, h, fill=SKIP, edge=LINE, lw=0.8, ls=(0, (3, 2)), radius=0.4)
        text_color = FADED
    else:
        box(ax, x, y, w, h, fill=tint(color, 0.62 if strong else 0.80),
            edge=color, lw=1.0, radius=0.4)
        text_color = INK
    label(ax, x + w / 2, y + h / 2 - 0.05, s, size=size, family=family,
          weight=weight, color=text_color)
    return w


def csv_lines(ax, x, y_top, size=7.5, h=3.3, gap=0.9):
    """Draw the example table as the lines of a CSV file. Returns the bottom y."""
    y = y_top
    for i, row in enumerate([NAMES] + ROWS):
        cx = x
        for j, value in enumerate(row):
            w = cell(ax, cx, y - h, value, COLORS[j], size=size, h=h, strong=(i == 0))
            cx = cx + w
            if j < 3:
                label(ax, cx + 0.45, y - h / 2 - 0.3, ',', size=size + 1, family=MONO)
                cx = cx + 0.9
        y = y - h - gap
    return y + gap


def column_chunk(ax, x, y, j, name_w=13.2, h=4.6, size=7.5, skipped=False):
    """Draw one column of the example table as it is stored in a Parquet file."""
    color = COLORS[j]
    if skipped:
        box(ax, x, y, name_w, h, fill=SKIP, edge=LINE, lw=0.8, ls=(0, (3, 2)), radius=0.4)
        name_color, type_color = FADED, FADED
    else:
        box(ax, x, y, name_w, h, fill=tint(color, 0.62), edge=color, radius=0.4)
        name_color, type_color = INK, DARK
    label(ax, x + name_w / 2, y + h * 0.67, NAMES[j], size=size, weight='bold',
          color=name_color)
    label(ax, x + name_w / 2, y + h * 0.27, TYPES[j], size=size, color=type_color)
    cx = x + name_w + 0.7
    for row in ROWS:
        w = cell(ax, cx, y + (h - 3.4) / 2, row[j], color, size=size, skipped=skipped)
        cx = cx + w + 0.5
    return cx


def panel_title(ax, x, y, title, subtitle=None):
    label(ax, x, y, title, size=10.5, weight='bold', ha='left')
    if subtitle:
        label(ax, x, y - 3.0, subtitle, size=8.5, color=MUTED, ha='left')


def flow_box(ax, x, y, w, h, s, fill=WHITE, edge=INK, lw=1.1, size=8.2,
             weight='normal'):
    box(ax, x, y, w, h, fill=fill, edge=edge, lw=lw, radius=0.9)
    label(ax, x + w / 2, y + h / 2, s, size=size, weight=weight)


# --------------------------------------------------------------------
# Figure 1: the same table stored row by row and column by column

def figure_row_column():
    fig, ax = new_figure(92, 41)
    top = 38
    panel_h = top - 8.5

    # CSV file
    panel_title(ax, 1.5, top, 'CSV file', 'stored row by row')
    box(ax, 1, 2, 40.5, panel_h, fill=WHITE, edge=LINE, radius=0.8, z=1)
    bottom = csv_lines(ax, 2.6, top - 8.4)
    label(ax, 2.6, bottom - 4.6, 'Plain text, one line per row.', size=8.5,
          color=MUTED, ha='left')
    label(ax, 2.6, bottom - 7.8, 'The data types are not stored.', size=8.5,
          color=MUTED, ha='left')

    # Parquet file
    px = 44.5
    panel_title(ax, px + 0.5, top, 'Parquet file', 'stored column by column')
    box(ax, px, 2, 46.5, panel_h, fill=WHITE, edge=LINE, radius=0.8, z=1)
    y = top - 8.4
    for j in range(4):
        column_chunk(ax, px + 1.6, y - 4.6, j)
        y = y - 5.4
    box(ax, px + 1.6, y - 5.3, 43.3, 5.3, fill=SOFT, edge=LINE, radius=0.4)
    label(ax, px + 2.8, y - 1.75, 'Footer', size=8, weight='bold', ha='left')
    label(ax, px + 2.8, y - 3.85, 'column names, data types, number of rows',
          size=8, color=DARK, ha='left')

    save(fig, 'row-vs-column.png')


# --------------------------------------------------------------------
# Figure 2: reading two columns from a CSV file and from a Parquet file

def figure_read_columns():
    fig, ax = new_figure(92, 42)

    label(ax, 46, 39.2, 'We want two columns:  county  and  spill_date', size=10.5,
          weight='bold')

    top = 33.5
    panel_h = top - 8.5

    # CSV file
    panel_title(ax, 1.5, top, 'CSV file', 'every line is read to find the two columns')
    box(ax, 1, 2, 40.5, panel_h, fill=WHITE, edge=LINE, radius=0.8, z=1)
    bottom = csv_lines(ax, 2.6, top - 8.4)
    box(ax, 2.6, bottom - 6.4, 15.5, 3.8, fill=INK, edge=INK, radius=0.4)
    label(ax, 2.6 + 7.75, bottom - 4.5, 'the whole file is read', size=7.6,
          color=WHITE, weight='bold')

    # Parquet file, with the two steps explained under the title
    px = 44.5
    panel_title(ax, px + 0.5, top, 'Parquet file')
    step(ax, px + 1.8, top - 3.1, 1, radius=1.25)
    label(ax, px + 3.7, top - 3.1, 'read the footer', size=8.5, color=MUTED, ha='left')
    step(ax, px + 17.6, top - 3.1, 2, radius=1.25)
    label(ax, px + 19.5, top - 3.1, 'read only the two columns', size=8.5,
          color=MUTED, ha='left')

    box(ax, px, 2, 46.5, panel_h, fill=WHITE, edge=LINE, radius=0.8, z=1)
    y = top - 8.4
    for j in range(4):
        skipped = j in (0, 3)
        column_chunk(ax, px + 5.0, y - 4.0, j, h=4.0, skipped=skipped)
        if not skipped:
            step(ax, px + 2.7, y - 2.0, 2)
        y = y - 4.6
    box(ax, px + 5.0, y - 3.9, 40.0, 3.9, fill=SOFT, edge=INK, lw=1.2, radius=0.4)
    label(ax, px + 6.2, y - 2.0, 'Footer:  where is each column stored?', size=8,
          ha='left')
    step(ax, px + 2.7, y - 1.95, 1)

    save(fig, 'read-columns.png')


# --------------------------------------------------------------------
# Figure 3: row groups and filters

def figure_row_groups():
    fig, ax = new_figure(86, 45)

    label(ax, 43, 42.2, 'We want the rows with  spill_date  from 2023 onwards',
          size=10.5, weight='bold')

    groups = [('Row group 1', 'spill_date from 1990 to 2004', True,
               'skipped: all its dates are before 2023'),
              ('Row group 2', 'spill_date from 2005 to 2016', True,
               'skipped: all its dates are before 2023'),
              ('Row group 3', 'spill_date from 2017 to 2026', False,
               'read, then the rows before 2023 are dropped')]

    x0 = 2
    box(ax, 1, 0.8, 84, 37.7, fill=WHITE, edge=LINE, radius=0.8, z=1)
    label(ax, 2.6, 35.6, 'A big Parquet file, with its rows sorted by date',
          size=10.5, weight='bold', ha='left')

    y = 32.5
    for name, stats, skipped, note in groups:
        h = 6.6
        box(ax, x0 + 0.6, y - h, 47.5, h, fill=(SKIP if skipped else WHITE),
            edge=(LINE if skipped else INK), lw=(0.8 if skipped else 1.2),
            ls=((0, (3, 2)) if skipped else '-'), radius=0.5)
        label(ax, x0 + 1.8, y - 1.7, name, size=8, weight='bold', ha='left',
              color=(FADED if skipped else INK))
        tx = x0 + 1.8
        for j in range(4):
            w = cell(ax, tx, y - h + 0.9, NAMES[j], COLORS[j], h=2.9, size=7.4,
                     pad=0.9, family=SANS, skipped=skipped)
            tx = tx + w + 0.6
        label(ax, x0 + 50.0, y - 2.1, stats, size=8, ha='left',
              color=(FADED if skipped else INK))
        label(ax, x0 + 50.0, y - 4.7, note, size=8, ha='left',
              color=(MUTED if skipped else INK),
              weight=('normal' if skipped else 'bold'))
        y = y - h - 1.3

    # Footer
    box(ax, x0 + 0.6, y - 6.4, 81.8, 6.4, fill=SOFT, edge=INK, lw=1.2, radius=0.5)
    label(ax, x0 + 1.8, y - 2.0, 'Footer', size=8, weight='bold', ha='left')
    label(ax, x0 + 1.8, y - 4.5,
          'for every row group: the smallest and largest value of each column',
          size=8, ha='left', color=DARK)

    save(fig, 'row-groups.png')


# --------------------------------------------------------------------
# Figure 4: why a column with repeated values takes little space

def figure_dictionary():
    fig, ax = new_figure(86, 40)

    values = ['Petroleum', 'Petroleum', 'Other', 'Petroleum', 'Petroleum',
              'Hazardous Material', 'Petroleum', 'Other']
    codes = {'Petroleum': '0', 'Other': '1', 'Hazardous Material': '2'}
    size = 8
    w = max([text_width(ax, value, size, MONO) for value in values]) + 4

    # Column written out in full
    label(ax, 2, 37, 'The column in a CSV file', size=10.5, weight='bold', ha='left')
    label(ax, 2, 34, 'every value is written out in full', size=8.5, color=MUTED,
          ha='left')
    y = 30.5
    for value in values:
        cell(ax, 2, y - 3.1, value, YELLOW, w=w, h=3.1, size=size)
        y = y - 3.5

    arrow(ax, 27.5, 16.5, 36.5, 16.5, lw=1.8)

    # Each different value once, plus a code per row
    label(ax, 40, 37, 'The column in a Parquet file', size=10.5, weight='bold',
          ha='left')
    label(ax, 40, 34, 'each different value is written once', size=8.5,
          color=MUTED, ha='left')
    y = 30.5
    for value, code in codes.items():
        cell(ax, 40, y - 3.1, code, YELLOW, w=4.2, h=3.1, size=size, strong=True)
        cell(ax, 44.9, y - 3.1, value, YELLOW, w=w, h=3.1, size=size)
        y = y - 3.5

    label(ax, 40, 16.3, 'and the rows only store a short code', size=8.5,
          color=MUTED, ha='left')
    x = 40
    for value in values:
        cell(ax, x, 9.6, codes[value], YELLOW, w=4.2, h=3.4, size=size, strong=True)
        x = x + 4.7

    label(ax, 40, 5.6, 'Then each column is compressed.', size=8.5, color=MUTED,
          ha='left')

    save(fig, 'column-compression.png')


# --------------------------------------------------------------------
# Figure 5: where Parquet fits in a workflow

def figure_workflow():
    fig, ax = new_figure(86, 44)

    w, h, gap = 13.4, 8.6, 3.2
    xs = [2 + i * (w + gap) for i in range(5)]

    def lane(y, steps, styles):
        for i, s in enumerate(steps):
            if styles[i] == 'file':
                flow_box(ax, xs[i], y, w, h, s, fill=SOFT, weight='bold')
            elif styles[i] == 'parquet':
                flow_box(ax, xs[i], y, w, h, s, fill=tint(BLUE, 0.80), edge=BLUE,
                         weight='bold')
            elif styles[i] == 'good':
                flow_box(ax, xs[i], y, w, h, s, fill=tint(BLUE, 0.90), edge=BLUE,
                         size=8)
            elif styles[i] == 'extra':
                flow_box(ax, xs[i], y, w, h, s, fill=tint(ORANGE, 0.82), edge=ORANGE,
                         size=8)
            else:
                flow_box(ax, xs[i], y, w, h, s)
            if i < 4:
                arrow(ax, xs[i] + w + 0.4, y + h / 2, xs[i + 1] - 0.4, y + h / 2)

    # Lane 1: CSV
    label(ax, 2, 41, 'Saving the clean data as a CSV file', size=10.5,
          weight='bold', ha='left')
    y1 = 28.5
    lane(y1,
         ['raw data\n(CSV)', 'clean:\nnames, codes,\ndates', 'clean data\n(CSV)',
          'read: data types\nare guessed,\nfix them again', 'analysis'],
         ['file', 'step', 'file', 'extra', 'step'])
    label(ax, xs[3] + w / 2, y1 - 2.4,
          'repeated in every notebook or script that reads the file', size=8,
          color=MUTED)

    # Divider
    ax.plot([2, 84], [21.5, 21.5], color=LINE, lw=0.8, zorder=1)

    # Lane 2: Parquet
    label(ax, 2, 17.5, 'Saving the clean data as a Parquet file', size=10.5,
          weight='bold', ha='left')
    y2 = 5.2
    lane(y2,
         ['raw data\n(CSV)', 'clean:\nnames, codes,\ndates', 'clean data\n(Parquet)',
          'read: same\ndata types,\nonly the columns\nand rows needed', 'analysis'],
         ['file', 'step', 'parquet', 'good', 'step'])
    label(ax, xs[3] + w / 2, y2 - 2.4,
          'nothing to fix: the file stores the data types', size=8, color=MUTED)

    save(fig, 'workflow.png')


# --------------------------------------------------------------------
# Figure 6: which format should I use?

def figure_decision():
    fig, ax = new_figure(86, 52)

    def question(x, y, w, h, s):
        box(ax, x, y, w, h, fill=WHITE, edge=INK, lw=1.1, radius=1.2)
        label(ax, x + w / 2, y + h / 2, s, size=8.6)

    def answer(x, y, w, h, name, note, parquet):
        if parquet:
            box(ax, x, y, w, h, fill=tint(BLUE, 0.80), edge=BLUE, lw=1.3, radius=1.2)
        else:
            box(ax, x, y, w, h, fill=SOFT, edge=INK, lw=1.1, radius=1.2)
        label(ax, x + w / 2, y + h * 0.68, name, size=10, weight='bold')
        label(ax, x + w / 2, y + h * 0.29, note, size=8, color=DARK)

    def branch(x1, y1, x2, y2, s, side):
        arrow(ax, x1, y1, x2, y2)
        offset = -1.2 if side == 'left' else 1.2
        label(ax, (x1 + x2) / 2 + offset, (y1 + y2) / 2 + 0.6, s, size=8.4,
              weight='bold', ha=('right' if side == 'left' else 'left'))

    # Level 1
    question(27, 42, 32, 7.5, 'Does the data have geometries\n(points, lines or polygons)?')

    # Level 2
    question(2, 23.5, 38, 9, 'Will someone open the file\nin a spreadsheet program\nor a text editor?')
    question(46, 23.5, 38, 9, 'Can whoever receives the file\nopen a GeoParquet file?')

    branch(36, 42, 21, 32.5, 'no', 'left')
    branch(50, 42, 65, 32.5, 'yes', 'right')

    # Level 3
    aw, ah = 18, 9
    answer(2, 4, aw, ah, 'CSV', 'plain text', False)
    answer(22, 4, aw, ah, 'Parquet', 'keeps the\ndata types', True)
    answer(46, 4, aw, ah, 'Shapefile', 'or the format\nthey ask for', False)
    answer(66, 4, aw, ah, 'GeoParquet', 'keeps the data\ntypes and CRS', True)

    branch(14, 23.5, 11, 13, 'yes', 'left')
    branch(28, 23.5, 31, 13, 'no', 'right')
    branch(58, 23.5, 55, 13, 'no', 'left')
    branch(72, 23.5, 75, 13, 'yes', 'right')

    save(fig, 'which-format.png')


# --------------------------------------------------------------------
# Figure 7: a shapefile and a GeoParquet file

def figure_shapefile_geoparquet():
    fig, ax = new_figure(86, 44)

    # Shapefile
    panel_title(ax, 1.5, 41, 'Shapefile', 'several files that must stay together')
    box(ax, 1, 2, 38, 33.5, fill=WHITE, edge=LINE, radius=0.8, z=1)
    files = [('.shp', 'geometries', AQUA),
             ('.dbf', 'table with the other columns', BLUE),
             ('.prj', 'CRS', YELLOW),
             ('.shx', 'index of the geometries', None),
             ('.cpg', 'text encoding', None)]
    y = 33.2
    for extension, content, color in files:
        h = 5.0
        if color is None:
            box(ax, 2.6, y - h, 34.8, h, fill=SOFT, edge=LINE, radius=0.5)
        else:
            box(ax, 2.6, y - h, 34.8, h, fill=tint(color, 0.80), edge=color, radius=0.5)
        label(ax, 4.0, y - h / 2, extension, size=8.6, family=MONO, weight='bold',
              ha='left')
        label(ax, 11.0, y - h / 2, content, size=8.4, ha='left')
        y = y - h - 1.1

    # GeoParquet
    px = 43
    panel_title(ax, px + 0.5, 41, 'GeoParquet', 'one file')
    box(ax, px, 2, 42, 33.5, fill=WHITE, edge=LINE, radius=0.8, z=1)
    columns = [('statefp', 'string', BLUE), ('name', 'string', BLUE),
               ('aland', 'integer', BLUE), ('geometry', 'geometry', AQUA)]
    y = 33.2
    for name, dtype, color in columns:
        h = 4.6
        box(ax, px + 1.6, y - h, 38.8, h, fill=tint(color, 0.80), edge=color, radius=0.5)
        label(ax, px + 3.0, y - h / 2, name, size=8.4, weight='bold', ha='left')
        label(ax, px + 39.0, y - h / 2, dtype, size=8, color=DARK, ha='right')
        if name == 'aland':
            label(ax, px + 21, y - h - 1.25, '...  more columns  ...', size=8,
                  color=MUTED)
            y = y - 2.4
        y = y - h - 0.9
    box(ax, px + 1.6, 3.6, 38.8, 5.6, fill=tint(YELLOW, 0.80), edge=YELLOW, radius=0.5)
    label(ax, px + 3.0, 7.3, 'Footer', size=8.4, weight='bold', ha='left')
    label(ax, px + 3.0, 5.0, 'column names, data types and CRS', size=8.2,
          ha='left', color=DARK)

    save(fig, 'shapefile-vs-geoparquet.png')


# --------------------------------------------------------------------

if __name__ == '__main__':
    figure_row_column()
    figure_read_columns()
    figure_row_groups()
    figure_dictionary()
    figure_workflow()
    figure_decision()
    figure_shapefile_geoparquet()

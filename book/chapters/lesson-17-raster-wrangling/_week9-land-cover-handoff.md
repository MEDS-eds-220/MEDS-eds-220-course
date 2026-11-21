# Week 9, class 1: land cover statistics (handoff)

Written 2026-11-20 (Friday). Class is **Tuesday, November 24**. Students need prep instructions by **Monday, November 23** (the week 8 page says "TBD: will be sent via Slack by Monday").

## Context

- We are ahead of schedule. The planned calendar had Fatiq lecturing this slot, but **Fatiq is no longer giving it**; the instructor teaches it.
- Week 9 has only this class (Thanksgiving Thursday and Friday). Week 10 Tuesday/Thursday cover workflows (notebook to `.py` scripts, branches).
- Chosen topic: **L16: land cover statistics** (`book/chapters/lesson-17-raster-wrangling/`), never taught this term, rebuilt on the **Eaton and Palisades fires** with the **Impact Observatory annual land cover maps (`io-lulc-annual-v02`)** from the Planetary Computer STAC.
- Why this topic: finishes the raster sequence (STAC + clipping, then pandas), covers the skipped "zonal statistics" class, and feeds the final project (Task 1 has a commented-out land cover option in `assignments/final-project.qmd`, lines ~68-75, that still points to Thomas Fire data).

## The draft notebook

`book/chapters/lesson-17-raster-wrangling/_lesson-16-io-lulc-eaton-palisades-SAMPLE.ipynb`

- The leading `_` keeps Quarto from rendering it (the site renders every `.ipynb`). It is committed on the `week9-class1` branch, together with this handoff document.
- It runs top to bottom in `eds220-env` and reads from `data/` next to it.
- Sections, in order: list comprehension aside, About the data (with a Drive download callout), Fire perimeter preparation, Catalog search, labels from the item metadata, Explore raster, Clip raster to geometry (no-data check, two-step clip), Categorical or continuous? (cuttable), Land cover statistics (exercises 1-9, solutions under each).

### Data it needs (all gitignored)

In `book/chapters/lesson-17-raster-wrangling/data/`:

- `Eaton_Perimeter_20250121/`, `Palisades_Perimeter_20250121/` (originals in `discussion-sections-upcoming/eaton-palisades/data/`)
- `ca_state_boundary/` (copied from `book/chapters/lesson-10-geopandas-intro/data/`)
- Also there, for the original `.qmd`: `California_Fire_Perimeters_2017/`, `GAP_National_Terrestrial_Ecosystems.csv`

**On the laptop:** check out the `week9-class1` branch for the notebook. The data folders are gitignored, so copy them over or download them from the course Drive.

### Decisions already made (don't re-open)

- **Dataset:** `io-lulc-annual-v02`, 2023 map (the newest; fires were January 2025). LANDFIRE EVT has GAP-level detail and is current, but it's ~1 GB and isn't on a STAC, and students should practice STAC access. The coarse 9 classes ("Rangeland" lumps chaparral, scrub and grassland) can be a discussion point.
- **Catalog search:** `datetime='2023'` returns two items, because the 2022 map's range ends on 2023-01-01. The notebook prints the time ranges, then selects with `item = items[0]` plus `assert item.properties['start_datetime'].startswith('2023')`.
- **Two-step clip stays** (`rio.clip_box()` then `rio.clip()`). In rioxarray 0.14.1, `rio.clip()` builds a mask the size of the whole raster (~5 billion pixels here). `from_disk=True` gave identical results but took 70 s against 1 s.
- **No-data:** this raster already declares 0 as no-data, so the old `RuntimeWarning` / `write_nodata` story and the "pay attention to warnings" callout are gone.
- **Colors:** official Planetary Computer colors (linked: `https://planetarycomputer.microsoft.com/api/data/v1/legend/classmap/io-lulc-9-class`), stored as a `color` column in `labels`, plotted with `.plot(levels=list(labels['code']) + [12], colors=list(labels['color']), add_colorbar=False)` and a legend from `mpatches.Patch`. Built-in colormaps (`tab10`) were tested and rejected: they still need `levels`, No Data handling and a legend, and the colors carry no meaning.
- **Bar plot:** classes above 1%, largest at top, percentage labels on the bars, no top/right spines.
- **List comprehensions** are not taught anywhere in EDS 220. EDS 217 shows them on Day 5 at reading level only. Don't name EDS 217 in student-facing text.

## To do

### The instructor's four reminders

1. **Go over the exercises** (Land cover statistics, exercises 1-9). Exercise 8 is an area sanity check: pixels give 56.9 km², the same as the perimeter. Exercise 9 repeats the analysis for Palisades.
2. **Move the list comprehension back in with getting the labels.** It is currently a section at the very top of the notebook. Move it back next to `class_values` / the `labels` cell.
3. **Create a CSV with the classes and colors** (`code`, `class_label`, `color`) that students can just read, to keep things simple. Put it on the course Drive and add it to the download callout. Then simplify the labels cell and the `labels['color']` cell. **Decide how this fits with item 2:** if the CSV supplies the labels, the list comprehension over `class_values` is no longer needed, unless it stays as "here's how the CSV was made".
4. **Make the instructor and student notebooks** (use the `instructor-notebook` skill; student notebook to the `MEDS-eds-220/student-notebooks` repo). Then write the prep instructions on `week-by-week/weekly-descriptions/week-9-2026.qmd`: which notebook to download, which data folders from the Drive (the two perimeter folders, `ca_state_boundary`, the new CSV).

### Also open

- **Week 9 page** (`week-9-2026.qmd`): it says "Class 18", but should be **Class 19** (week 8 already used 18). Remove the "TA lecture" comment, fill in the class, and add week 9 to the "week by week" navbar menu in `_quarto.yml`.
- **Course Drive:** upload the Eaton/Palisades perimeter folders, `ca_state_boundary` and the new CSV. Check the folder names match the notebook's download callout.
- **Perimeter source:** the notebook has a TODO for the Eaton/Palisades perimeter source and citation. Add a `references/references.bib` entry when this becomes the `.qmd`.
- **Week 8 page** still says the next class's prep is TBD.
- **Original `lesson-17-raster-wrangling.qmd`** has edits from this session (committed on `week9-class1`):
  - `/fix-typos`: spelling, grammar, exercise renumbering 1-7, km².
  - Audit fixes: rioxarray links moved to `vylor.github.io/rioxarray/stable/…`; About the data now says three datasets, with a Drive callout using `{{< var shared-data-folder >}}`; hidden solutions turned into `#| include: false` cells; YAML header with `toc-title`; `print(lulc.dtype)`.
  - It has **not been re-rendered**. The data is now in place on the desktop, so `quarto render book/chapters/lesson-17-raster-wrangling/lesson-17-raster-wrangling.qmd` should work there. Commit the source, `_freeze/` and `docs/` together.
  - **Decide:** does the notebook replace this `.qmd` (Eaton/Palisades version), or does the GAP/Thomas Fire version stay?
- **Remaining audit items on the original `.qmd`** (most are already solved in the notebook): no learning objectives or intro; 0 described as no-data although the raster declares none; categorical data shown with a continuous colormap; exercises never say to drop code 0; pixel × 900 m² holds only because of the equal-area Albers CRS; `iloc[43:47]` picks the Developed rows by position; no area sanity check; "spatial_ref = 0" plot title. Also the **lesson numbering**: rioxarray is titled 17 and STAC 18, but this lesson is titled 16, though it comes after both.
- **Review tracker:** run `/mark-reviewed` for L16 (typos done; audit partly incorporated).
- **Week pages 0, 4 and 7** hard-code the Drive URL instead of `{{< var shared-data-folder >}}`.

### Later (week 10 and summer)

- Week 10 workflows lesson: a natural place for output formats (`to_file`, GeoParquet, writing rasters), including the skipped parquet/GeoParquet class. The land cover notebook is good material for the notebook-to-script refactor.
- Gaps not taught anywhere: raster reprojection/alignment (`rio.reproject`, `reproject_match`, nearest resampling for categorical data), measuring geometry (`.area`, `.length`), spatial joins (`sjoin`), raster time series (`groupby('time.month')`). KML is low priority (about 10 minutes; `gpd.read_file` reads it).
- The unused aggregation (`coarsen`) section is in `book/chapters/_lesson-16-aggregation.qmd`. It needs a home or deleting.

"""Build the scratch notebook for the proposed final project Task 2 (LA28 urban heat).

Run from the repo root with eds220-env active:
    python assignments/_final-project-heat/build-notebook.py
Then execute:
    python -m jupyter nbconvert --to notebook --execute --inplace \
        assignments/_final-project-heat/la28-heat-scratch.ipynb
"""
import nbformat as nbf
from pathlib import Path

HERE = Path(__file__).parent
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

NEW = "🆕 **Not covered in class:**"

md(f"""
# Urban heat at LA28 Olympic venues (scratch solution)

**Proposed final project Task 2. Scratch notebook for the instructor, not student-facing.**

Every place students need something we haven't covered in class is marked with {NEW}

Summary of what's new for students:

1. Filtering a STAC search by cloud cover (`query=` parameter).
2. Choosing one item out of several that intersect the area (pick the one whose footprint contains the whole city).
3. Reading the scale and offset from the STAC metadata and converting the raster to degrees Celsius. The values stored in the file are integers, and the file's own attributes say `scale_factor: 1.0`, which is wrong for this product.
4. Buffering points (`.buffer()`) to turn venue locations into areas.
5. Calculating a statistic per polygon (a simple loop over venues with `rio.clip()`).

Everything else (STAC access with `pystac_client`, `open_rasterio` from an asset href, `squeeze`, `clip_box` + `clip`, no-data values, `points_from_xy`, `to_crs`, `contextily`) was covered in lessons 11 to 17 or discussion section 8.
""")

md("""
## About

**Event.** NASA JPL's ECOSTRESS team is working with the LA28 Olympics committee on heat mitigation for venues, transportation corridors and pedestrian areas ahead of the 2028 Games. They released a map of afternoon street temperatures in Los Angeles. In this task you will make a similar (simpler) analysis with Landsat data: how hot does the ground get around LA28 venues compared to the city as a whole?

**Question.** On a clear late-summer day, which LA28 venues sit in areas hotter than the city average, and how much of the area around each venue is hotter than average?

**Why Landsat and not ECOSTRESS?** ECOSTRESS is not on the Microsoft Planetary Computer and needs a NASA Earthdata account. Landsat Collection 2 Level-2 includes a surface temperature band and needs no account.
""")

md("""
## About the data

1. **Landsat Collection 2 Level-2 surface temperature** (`landsat-c2-l2` collection, `lwir11` asset), from the Microsoft Planetary Computer STAC catalog. Pixels are 30 m, resampled from the thermal sensor's native 100 m.
2. **Los Angeles city boundary**: US Census Bureau TIGER/Line 2025 Places shapefile for California (`tl_2025_06_place.zip`, downloaded from https://www2.census.gov/geo/tiger/TIGER2025/PLACE/).
3. **LA28 venue locations**: coordinates typed in by hand from the LA28 venue list.

> **Instructor note:** I typed the venue coordinates from memory of well-known stadium locations. Check them against the official LA28 venue list before giving this to students, and check which events each venue will host.
""")

md("## Setup")
code("""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import rioxarray as rioxr
import contextily as ctx

from shapely.geometry import shape  # To turn GeoJSON dictionaries into geometries
from pystac_client import Client
import planetary_computer
""")

md("""
## Polygons: Los Angeles city boundary

The Census Places shapefile has every city in California. We keep only Los Angeles.
""")
code("""
places = gpd.read_file('data/tl_2025_06_place.zip')
la = places[places['NAME'] == 'Los Angeles']

print(la.crs)
la.plot()
""")

md("""
## Polygons: LA28 venues

We create a data frame with the venue coordinates and turn it into a geo-data frame, as in lesson 11.
""")
code("""
venues = pd.DataFrame({
    'venue': ['LA Memorial Coliseum', 'SoFi Stadium', 'Intuit Dome',
              'Crypto.com Arena', 'Dodger Stadium', 'Rose Bowl'],
    'lon': [-118.2879, -118.3392, -118.3410, -118.2673, -118.2400, -118.1676],
    'lat': [34.0141, 33.9535, 33.9450, 34.0430, 34.0739, 34.1613],
})

venues = gpd.GeoDataFrame(venues,
                          geometry=gpd.points_from_xy(venues['lon'], venues['lat']),
                          crs='epsg:4326')
venues
""")

md(f"""
{NEW} buffering. A venue is a point, but we want the temperature of the area around it. `.buffer(500)` draws a circle with a 500 m radius around each point.

The buffer distance is in the units of the CRS, so we must reproject to a projected CRS in meters first. Buffering in EPSG:4326 would give a radius of 500 *degrees*. We use UTM zone 11N (EPSG:32611), which is also the Landsat raster's CRS.
""")
code("""
venues = venues.to_crs('epsg:32611')
venues['geometry'] = venues.buffer(500)

fig, ax = plt.subplots()
la.to_crs(venues.crs).plot(ax=ax, color='lightgray')
venues.plot(ax=ax, color='red')
plt.show()
""")

md("""
The Rose Bowl (Pasadena) and SoFi Stadium and Intuit Dome (Inglewood) are outside the City of Los Angeles. We keep them: our comparison is "venue vs. city average", not "venues inside the city".
""")

md("## STAC search: Landsat surface temperature")
code("""
catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# Bounding box of LA in lat/lon, as the search expects
la_bbox = list(la.to_crs('epsg:4326').total_bounds)
""")

md(f"""
{NEW} filtering a search by item properties. Clouds hide the ground from the thermal sensor, so we only want nearly cloud-free scenes. The `query` parameter filters items by any property in their metadata, here `eo:cloud_cover` (a percentage).
""")
code("""
search = catalog.search(
    collections=['landsat-c2-l2'],
    bbox=la_bbox,
    datetime='2026-06-01/2026-09-30',
    query={'eo:cloud_cover': {'lt': 10}},
)
items = search.item_collection()
len(items)
""")

md(f"""
{NEW} choosing between overlapping scenes. Landsat scenes are tiles, and LA sits near the edge between two of them. A search can return tiles that only cover part of the city (it did for a single-date search while I was testing), so we check which footprints contain the whole city, using `shape()` from lesson 16.
""")
code("""
la_4326 = la.to_crs('epsg:4326').geometry.iloc[0]

for item in items:
    footprint = shape(item.geometry)
    print(item.id,
          item.properties['eo:cloud_cover'],
          'covers LA:', footprint.contains(la_4326))
""")

md("""
We pick the scene from **August 21, 2026** (Landsat 8): it covers all of LA and has the lowest cloud cover.

> **Student decision:** which date to use. Any clear summer scene works. Students should say why they picked theirs (cloud cover, heat wave, time of year).
""")
code("""
item = [i for i in items if i.id == 'LC08_L2SP_041036_20260821_02_T1'][0]

print(item.properties['datetime'])
""")

md("""
The time is in UTC: 18:28 UTC is **11:28 am** in Los Angeles. Landsat always passes over in the late morning, before the hottest part of the day. ECOSTRESS's map averaged 1 to 4 pm.
""")

md("## Surface temperature raster")
code("""
for key in item.assets.keys():
    print(key, '--', item.assets[key].title)
""")
code("""
lst = rioxr.open_rasterio(item.assets['lwir11'].href)
lst = lst.squeeze('band', drop=True)

print('CRS:', lst.rio.crs)
print('Resolution:', lst.rio.resolution())
print('No-data value:', lst.rio.nodata)
print('Data type:', lst.dtype)
print('Attributes:', lst.attrs)
""")

md(f"""
{NEW} scale and offset. The values are `uint16` integers, not temperatures. To save space, Landsat stores each temperature as an integer, and we have to convert it back with:

$$\\text{{temperature (K)}} = \\text{{value}} \\times \\text{{scale}} + \\text{{offset}}$$

Notice the file's own attributes say `scale_factor: 1.0` and `add_offset: 0.0`. That is **not** right for this product. The real values are in the STAC metadata for the asset:
""")
code("""
item.assets['lwir11'].extra_fields['raster:bands']
""")

md("""
## Clip to Los Angeles

As in lesson 17: match the CRS, clip to the bounding box first, then to the polygon.
""")
code("""
la = la.to_crs(lst.rio.crs)
assert la.crs == lst.rio.crs

lst_la = lst.rio.clip_box(*la.total_bounds).rio.clip(la.geometry)
""")

md("""
Now convert to °C. The no-data value is 0, and `rio.clip()` filled everything outside LA with 0. **We must turn the 0s into NaN before converting**, or they become -124 °C and drag every average down.
""")
code("""
band = item.assets['lwir11'].extra_fields['raster:bands'][0]

lst_la = lst_la.where(lst_la != band['nodata'])            # 0 -> NaN
lst_la = lst_la * band['scale'] + band['offset'] - 273.15   # integers -> K -> °C

lst_la.plot(cmap='inferno', cbar_kwargs={'label': 'Surface temperature (°C)'})
""")

md("""
Quick check that the values make sense:
""")
code("""
print(f"Min: {float(lst_la.min()):.1f} °C")
print(f"Max: {float(lst_la.max()):.1f} °C")
print(f"Mean: {float(lst_la.mean()):.1f} °C")
""")

md("""
> **Data check for students:** what are the coldest pixels (below 25 °C)? On the plot they are the ocean: **the TIGER boundary of Los Angeles includes water** (Santa Monica Bay off Venice, and the harbor). Those pixels pull the city average down. Students could notice this and decide what to do, e.g. use the Census *cartographic boundary* file, which follows the shoreline, or mask out water. I left the water in for this scratch version.
>
> The hottest pixels are rooftops and parking lots. Surface temperatures of 50+ °C are normal for asphalt on a summer day. **This is the temperature of the ground, not of the air.** Air temperature over hot pavement is usually much lower.
""")

md("""
## Statistics: venues vs. the city average

The city average is our reference.

> **Student decision:** the threshold. "Hotter than the city average" is a simple choice; a fixed temperature (e.g. 50 °C) or a percentile are others. Students should justify theirs.
""")
code("""
city_mean = float(lst_la.mean())
city_mean
""")

md(f"""
{NEW} statistics per polygon. We clip the raster to each venue's buffer, one at a time. We start from a box around all the venues so each clip is fast.
""")
code("""
# Small raster covering all venues, converted to °C
lst_venues = lst.rio.clip_box(*venues.total_bounds)
lst_venues = lst_venues.where(lst_venues != band['nodata'])
lst_venues = lst_venues * band['scale'] + band['offset'] - 273.15

mean_temps = []
pct_hot = []

for geom in venues.geometry:
    venue_lst = lst_venues.rio.clip([geom])
    n_pixels = int(venue_lst.notnull().sum())
    n_hot = int((venue_lst > city_mean).sum())

    mean_temps.append(float(venue_lst.mean()))
    pct_hot.append(n_hot / n_pixels * 100)

venues['mean_temp_c'] = mean_temps
venues['pct_above_city_mean'] = pct_hot

venues[['venue', 'mean_temp_c', 'pct_above_city_mean']].round(1).sort_values('mean_temp_c', ascending=False)
""")

md("""
Each 500 m buffer covers about 870 Landsat pixels, but the thermal sensor's real resolution is 100 m, so each buffer holds only about 80 independent measurements.
""")

md("""
## Map

Surface temperature over LA with the venue buffers and a basemap (contextily, as in discussion section 8).
""")
code("""
fig, ax = plt.subplots(figsize=(9, 8))

lst_la.plot(ax=ax, cmap='inferno', alpha=0.85,
            cbar_kwargs={'label': 'Surface temperature (°C)', 'shrink': 0.7})
la.boundary.plot(ax=ax, color='black', linewidth=0.6)
venues.boundary.plot(ax=ax, color='cyan', linewidth=2)

for x, y, name in zip(venues.centroid.x, venues.centroid.y, venues['venue']):
    ax.annotate(name, (x, y), xytext=(6, 6), textcoords='offset points',
                color='white', fontsize=8, fontweight='bold')

# Zoom out enough to show the venues outside the city
xmin, ymin, xmax, ymax = la.total_bounds
ax.set_xlim(xmin - 2000, xmax + 8000)
ax.set_ylim(ymin - 2000, ymax + 2000)

ctx.add_basemap(ax, crs=la.crs, source=ctx.providers.Esri.WorldStreetMap, attribution_size=6)

ax.set_title('Surface temperature, Los Angeles, Aug 21, 2026, 11:28 am\\n'
             'LA28 venues (500 m buffers) in cyan')
ax.set_axis_off()
plt.show()
""")

md("""
## Possible reflection questions for students

1. Landsat measured at 11:28 am. Would you expect the ranking of venues to change in the late afternoon? Why might ECOSTRESS be better for this question?
2. Is surface temperature a good measure of heat risk for spectators? What would you need to know besides it?
3. The thermal band is 100 m resampled to 30 m. Is a single stadium resolved in this data?
4. How would your results change on a different date? Try one more scene.
""")

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3 (ipykernel)', 'language': 'python'}
nbf.write(nb, HERE / 'la28-heat-scratch.ipynb')
print('Wrote', HERE / 'la28-heat-scratch.ipynb')

"""Build the draft solution notebook for the proposed final project Task 2 (LA28 urban heat).

Run from the repo root with eds220-env active:
    python assignments/_final-project-heat/build-notebook.py
Then execute:
    python -m jupyter nbconvert --to notebook --execute --inplace \
        assignments/_final-project-heat/la28-heat-scratch.ipynb

Data in assignments/_final-project-heat/data/ (gitignored):
- la28-facilities.csv: the 19 permanent, on-land LA28 facilities given to students.
  Built in la28-venues-polygons.ipynb (LA28 venue pages cross-referenced with Wikipedia,
  coordinates from OpenStreetMap).
- tl_2025_us_uac20.zip: Census TIGER/Line 2025, 2020 urban areas (national file, ~74 MB).
"""
import nbformat as nbf
from pathlib import Path

HERE = Path(__file__).parent
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

NEW = "🆕 **Not covered in class:**"

md(f"""
# Urban heat at LA28 facilities (draft solution)

**Proposed final project Task 2. Draft solution for the instructor, not student-facing.**

Every place students need something we haven't covered in class is marked with {NEW}

Summary of what's new for students:

1. Filtering a STAC search by cloud cover (`query=` parameter).
2. Checking that a scene's footprint covers all the facilities.
3. Reading the scale and offset from the STAC metadata to convert the raster to degrees Celsius. The file itself doesn't record them, so rioxarray shows the defaults (scale 1, offset 0).
4. Buffering points (`.buffer()`) to turn facility locations into areas.
5. Calculating a statistic per polygon (a loop over facilities with `rio.clip()`).

Everything else (STAC access with `pystac_client`, `open_rasterio` from an asset href, `squeeze`, `clip_box` + `clip`, no-data values, `points_from_xy`, `to_crs`, `contextily`, pandas plotting) was covered in lessons 4 and 11 to 17 or discussion section 8.
""")

md("""
## About

**Event.** NASA JPL's ECOSTRESS team is working with the LA28 Olympics committee on heat mitigation for venues, transportation corridors and pedestrian areas ahead of the 2028 Games. In this task you will make a similar (simpler) analysis with Landsat data: how hot does the ground get around LA28 facilities compared to the Los Angeles urban area as a whole?

**Question.** On a clear late-summer day, which LA28 facilities sit in areas hotter than the urban area's average, and how much of the area around each facility is hotter than that average?

We answer it in **relative** terms: degrees above or below the urban average *on the same date*. Absolute surface temperatures change a lot from one day to the next (see below), but comparisons within one scene are more robust.

**Why Landsat and not ECOSTRESS?** ECOSTRESS is not on the Microsoft Planetary Computer and needs a NASA Earthdata account. Landsat Collection 2 Level-2 includes a surface temperature band and needs no account.
""")

md("""
## About the data

1. **Landsat Collection 2 Level-2 surface temperature** (`landsat-c2-l2` collection, `lwir11` asset), from the Microsoft Planetary Computer STAC catalog. Pixels are 30 m, resampled from the thermal sensor's native 100 m. Each pixel also has an uncertainty estimate, in kelvin, in the `qa` asset.

    **Surface temperature is not air temperature.** Landsat measures the thermal radiation coming off the top millimeter of whatever it sees from above: roofs, pavement, treetops, grass, water. Dark pavement and roofs in full sun often reach 50 to 70 °C, while the air a few feet above them is much cooler. Air temperature (what a weather station reports) is measured in the shade, about 2 m above the ground, and changes much more slowly across a city. Some consequences for this analysis:
    - the satellite sees the top of a roof or a tree canopy, not the shaded sidewalk where people stand;
    - converting radiation to temperature requires assuming how efficiently each surface emits heat (its *emissivity*); this is hard for urban materials such as metal roofs and is the main source of uncertainty;
    - dry grass and bare soil get almost as hot as pavement by late summer, while irrigated grass stays cool;
    - surface temperature is a good indicator of where the built environment stores heat (and where shade or vegetation would help), but it is not a direct measure of how hot people feel.

2. **Census 2020 urban areas**, US Census Bureau TIGER/Line 2025 shapefile (`tl_2025_us_uac20.zip`, https://www2.census.gov/geo/tiger/TIGER2025/UAC20/). We use the *Los Angeles--Long Beach--Anaheim, CA* urban area as our reference area: the Census defines it as continuously built-up land, so its average temperature represents the city people live in, without the mountains, desert or ocean that a county or city boundary would include.

3. **LA28 facilities** (`la28-facilities.csv`, provided). The 19 **permanent, on-land** LA28 competition facilities in the Los Angeles area, with approximate coordinates. The list comes from the LA28 venue list cross-referenced with Wikipedia's venue statuses. It leaves out:
    - temporary venues (e.g. Venice Beach, Sepulveda Basin, the Long Beach Convention Center lot), since Landsat can only see what is built today;
    - water venues (Port of Los Angeles, Long Beach Marine Stadium, Belmont Pier), since over water Landsat measures the water surface;
    - venues outside the LA area (Trestles, Oklahoma City and the football stadiums in other cities).
""")

md("## Setup")
code("""
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
## Reference area: Los Angeles urban area

The file has every urban area in the US. We keep only Los Angeles.
""")
code("""
urban = gpd.read_file('data/tl_2025_us_uac20.zip')
urban = urban[urban['NAME20'] == 'Los Angeles--Long Beach--Anaheim, CA']

print(urban.crs)
print(f"Land area: {urban['ALAND20'].iloc[0] / 1000**2:,.0f} km²")
print(f"Water area: {urban['AWATER20'].iloc[0] / 1000**2:,.0f} km²")
urban.plot()
""")

md("""
## LA28 facilities

We read the CSV and turn it into a geo-data frame, as in lesson 11.
""")
code("""
facilities = pd.read_csv('data/la28-facilities.csv')
facilities = gpd.GeoDataFrame(facilities,
                              geometry=gpd.points_from_xy(facilities['lon'], facilities['lat']),
                              crs='epsg:4326')
facilities[['facility', 'city', 'sports']]
""")

md("Check that every facility is inside the urban area:")
code("""
facilities.within(urban.to_crs(facilities.crs).geometry.iloc[0]).all()
""")

md(f"""
{NEW} buffering. A facility is a point, but we want the temperature of the area around it. `.buffer(500)` draws a circle with a 500 m radius around each point.

The buffer distance is in the units of the CRS, so we must reproject to a projected CRS in meters first. Buffering in EPSG:4326 would give a radius of 500 *degrees*. We use UTM zone 11N (EPSG:32611), which is also the Landsat raster's CRS.
""")
code("""
facilities = facilities.to_crs('epsg:32611')
facilities['geometry'] = facilities.buffer(500)

fig, ax = plt.subplots()
urban.to_crs(facilities.crs).plot(ax=ax, color='lightgray')
facilities.plot(ax=ax, color='red')
plt.show()
""")

md("""
> **Student decision:** the buffer size. In downtown LA, Crypto.com Arena, Peacock Theater and the LA Convention Center are 200 to 400 m apart, so their 500 m buffers overlap almost completely and give nearly the same numbers. A smaller buffer separates them but holds fewer pixels.
""")

md("## STAC search: Landsat surface temperature")
code("""
catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# Bounding box of the urban area in lat/lon, as the search expects
urban_bbox = list(urban.to_crs('epsg:4326').total_bounds)
""")

md(f"""
{NEW} filtering a search by item properties. Clouds hide the ground from the thermal sensor, so we only want nearly cloud-free scenes. The `query` parameter filters items by any property in their metadata, here `eo:cloud_cover` (a percentage).
""")
code("""
search = catalog.search(
    collections=['landsat-c2-l2'],
    bbox=urban_bbox,
    datetime='2026-06-01/2026-09-30',
    query={'eo:cloud_cover': {'lt': 10}},
)
items = search.item_collection()
len(items)
""")

md(f"""
{NEW} checking a scene's coverage. Landsat scenes are tiles, and the LA urban area sits near the corner of one. We check which footprints contain all the facilities, using `shape()` from lesson 16.
""")
code("""
facilities_4326 = facilities.to_crs('epsg:4326')

for item in items:
    footprint = shape(item.geometry)
    print(item.id,
          item.properties['eo:cloud_cover'],
          'covers all facilities:', facilities_4326.within(footprint).all())
""")

md("""
We pick the scene from **August 21, 2026** (Landsat 8): it covers all facilities and has the lowest cloud cover.

> **Instructor note:** the scene covers about 99% of the urban area. A sliver at the southeastern tip (around Laguna Niguel) is outside it and comes out as no-data. It doesn't affect the facilities and barely changes the urban average.

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

The attributes above show `scale_factor: 1.0` and `add_offset: 0.0`. Those are rioxarray's defaults: the file doesn't record how to convert its integers, so a scale of 1 would give values around 47,000 K. The real scale and offset are in the STAC metadata for the asset:
""")
code("""
item.assets['lwir11'].extra_fields['raster:bands']
""")

md("""
## Clip to the urban area

As in lesson 17: match the CRS, clip to the bounding box first, then to the polygon.
""")
code("""
urban = urban.to_crs(lst.rio.crs)
assert urban.crs == lst.rio.crs

lst_urban = lst.rio.clip_box(*urban.total_bounds).rio.clip(urban.geometry)
""")

md("""
Now convert to °C. The no-data value is 0, and `rio.clip()` filled everything outside the urban area with 0. **We must turn the 0s into NaN before converting**, or they become -124 °C and drag every average down.
""")
code("""
band = item.assets['lwir11'].extra_fields['raster:bands'][0]

lst_urban = lst_urban.where(lst_urban != band['nodata'])           # 0 -> NaN
lst_urban = lst_urban * band['scale'] + band['offset'] - 273.15   # integers -> K -> °C

lst_urban.plot(cmap='inferno', cbar_kwargs={'label': 'Surface temperature (°C)'})
""")

md("Quick check that the values make sense:")
code("""
print(f"Min: {float(lst_urban.min()):.1f} °C")
print(f"Max: {float(lst_urban.max()):.1f} °C")
print(f"Mean: {float(lst_urban.mean()):.1f} °C")
""")

md("""
> **Data check for students:** surface temperatures of 50+ °C are normal for asphalt and rooftops on a summer day. **This is the temperature of the ground, not of the air.** The hottest pixels (60 to 70 °C, less than 0.1% of the area) are airport runways and large warehouse roofs, e.g. around Ontario Airport and Van Nuys Airport. The coolest pixels are water the urban area still includes (reservoirs, harbor channels) and irrigated green spaces.

> **Instructor note: absolute values depend on the date.** Urban-area mean surface temperature on the other clear 2026 scenes I checked: Jun 10: 46.1 °C, Aug 5: 42.4 °C, **Aug 21: 48.7 °C**, Sep 14: 40.1 °C, Sep 22: 38.3 °C. This is why we report results relative to the urban average on the same date.
""")

md("""
## How uncertain are these temperatures?

The `qa` asset holds Landsat's own estimate of the uncertainty of each surface temperature pixel, in kelvin (a difference of 1 K is the same as 1 °C). It is stored as integers too, so we use the same scale-and-offset steps, with its own metadata:
""")
code("""
item.assets['qa'].extra_fields['raster:bands']
""")
code("""
qa_band = item.assets['qa'].extra_fields['raster:bands'][0]

st_uncertainty = rioxr.open_rasterio(item.assets['qa'].href).squeeze('band', drop=True)
st_uncertainty = st_uncertainty.rio.clip_box(*urban.total_bounds).rio.clip(urban.geometry)
st_uncertainty = st_uncertainty.where(st_uncertainty != qa_band['nodata'])   # -9999 -> NaN
st_uncertainty = st_uncertainty * qa_band['scale']                          # integers -> K

st_uncertainty.plot(cmap='viridis', robust=True, cbar_kwargs={'label': 'Uncertainty (K)'})
""")
code("""
print(f"Median uncertainty: {float(st_uncertainty.median()):.1f} K")
print(f"90% of pixels have uncertainty below: {float(st_uncertainty.quantile(0.9)):.1f} K")
""")

md("""
A typical pixel's temperature is uncertain by about ±2 °C. Keep this number in mind: a facility that is 1 °C warmer than the urban average is **not clearly different** from it.

Averaging many pixels in a buffer reduces random errors, but not systematic ones (for example, an emissivity assumption that is wrong for a whole type of roof). So we use the typical pixel uncertainty as a conservative error bar.

The uncertainty is not the same everywhere: it is much higher along the coast (above 4 K), where water and land mix within pixels and the air holds more moisture. Facilities near the coast, such as Long Beach Arena, will have larger error bars.
""")

md("""
## Statistics: facilities vs. the urban area

The urban area's average is our reference.

> **Student decision:** the threshold. "Hotter than the urban average" is a simple choice; a fixed temperature (e.g. 50 °C) or a percentile are others. Students should justify theirs.
""")
code("""
urban_mean = float(lst_urban.mean())
urban_mean
""")

md(f"""
{NEW} statistics per polygon. We clip the temperature raster to each facility's buffer, one at a time. Every facility is inside the urban area, so we can clip `lst_urban` directly.
""")
code("""
mean_temps = []
pct_hot = []
uncertainties = []

for geom in facilities.geometry:
    facility_lst = lst_urban.rio.clip([geom])
    n_pixels = int(facility_lst.notnull().sum())
    n_hot = int((facility_lst > urban_mean).sum())

    mean_temps.append(float(facility_lst.mean()))
    pct_hot.append(n_hot / n_pixels * 100)
    uncertainties.append(float(st_uncertainty.rio.clip([geom]).mean()))

facilities['mean_temp_c'] = mean_temps
facilities['pct_above_urban_mean'] = pct_hot
facilities['uncertainty_k'] = uncertainties

# Relative result: difference from the urban average
facilities['diff_from_urban_c'] = facilities['mean_temp_c'] - urban_mean

# Is the difference larger than the uncertainty?
facilities['clearly_different'] = facilities['diff_from_urban_c'].abs() > facilities['uncertainty_k']

results = (facilities[['facility', 'city', 'diff_from_urban_c', 'uncertainty_k',
                       'clearly_different', 'pct_above_urban_mean']]
           .sort_values('diff_from_urban_c', ascending=False)
           .round(1))
results
""")

md("""
Each 500 m buffer covers about 870 Landsat pixels, but the thermal sensor's real resolution is 100 m, so each buffer holds only about 80 independent measurements.
""")

md("""
We plot each facility's difference from the urban average, with the uncertainty as error bars. Positive means hotter than the urban area. Bars whose error bar crosses 0 are not clearly different from the urban average.
""")
code("""
plot_data = results.set_index('facility').sort_values('diff_from_urban_c')
colors = ['tab:red' if d > 0 else 'tab:blue' for d in plot_data['diff_from_urban_c']]

ax = plot_data['diff_from_urban_c'].plot.barh(figsize=(7, 7), color=colors,
                                              xerr=plot_data['uncertainty_k'], capsize=3)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel(f'Mean surface temperature within 500 m minus urban average ({urban_mean:.1f} °C)')
ax.set_ylabel('')
ax.set_title('Surface temperature around LA28 facilities\\nAug 21, 2026, 11:28 am')
plt.show()
""")

md("""
## Map

Surface temperature over the urban area with the facility buffers and a basemap (contextily, as in discussion section 8).
""")
code("""
fig, ax = plt.subplots(figsize=(10, 8))

lst_urban.plot(ax=ax, cmap='inferno', alpha=0.85,
               cbar_kwargs={'label': 'Surface temperature (°C)', 'shrink': 0.7})
urban.boundary.plot(ax=ax, color='black', linewidth=0.5)
facilities.boundary.plot(ax=ax, color='cyan', linewidth=1.5)

ctx.add_basemap(ax, crs=urban.crs, source=ctx.providers.Esri.WorldStreetMap, attribution_size=6)

ax.set_title('Surface temperature, Los Angeles urban area, Aug 21, 2026, 11:28 am\\n'
             'Permanent LA28 facilities (500 m buffers) in cyan')
ax.set_axis_off()
plt.show()
""")

md("""
## Possible reflection questions for students

1. Landsat measured at 11:28 am. Would you expect the ranking of facilities to change in the late afternoon? Why might ECOSTRESS be better for this question?
2. Is surface temperature a good measure of heat risk for spectators? What would you need to know besides it (air temperature, humidity, shade, time spent outdoors)?
3. How many facilities are clearly different from the urban average once you account for uncertainty? What does that mean for how you would communicate these results?
4. The thermal band is 100 m resampled to 30 m, and some buffers overlap. Is each facility really measured separately?
5. Water venues were left out. Why would a buffer around Long Beach Marine Stadium be cooler than one around the Coliseum, and why isn't that a fair comparison?
6. The hottest facilities (Fairplex, Honda Center, Santa Anita) are all inland, and the coolest are near the coast or on irrigated grass (Riviera Country Club). Is the difference about the facilities themselves, or about where they are? How could you tell?
7. How would your results change on a different date? Try one more scene.
""")

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3 (ipykernel)', 'language': 'python'}
nbf.write(nb, HERE / 'la28-heat-scratch.ipynb')
print('Wrote', HERE / 'la28-heat-scratch.ipynb')

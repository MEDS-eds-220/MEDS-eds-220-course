"""Build the LA28 venues + reference polygons scratch notebook.

Run from the repo root with eds220-env active:
    python assignments/_final-project-heat/build-venues-notebook.py
    python -m jupyter nbconvert --to notebook --execute --inplace \
        assignments/_final-project-heat/la28-venues-polygons.ipynb

Data in assignments/_final-project-heat/data/ (gitignored):
- la28-venues-scraped.json: zone, sports and description scraped from every
  https://la28.org/en/games-plan/venues/<slug>.html page on 2026-11-23.
- la28-venues.csv: the same 49 venues plus OpenStreetMap (Nominatim) coordinates
  for the 41 Southern California venues. Geocoding queries use each venue's real
  name (e.g. "DTLA Arena" -> Crypto.com Arena). Two were fixed by hand
  (Trestles matched a clothing store; Allianz Beach Arena matched the wrong end
  of the Long Beach shore).
- tl_2025_06_place.zip, tl_2025_us_county.zip, tl_2025_us_uac20.zip: Census TIGER/Line 2025.
"""
import nbformat as nbf
from pathlib import Path

HERE = Path(__file__).parent
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md("""
# LA28 venues and reference polygons (scratch, instructor only)

Goal: list every LA28 venue, see which cities and counties they fall in, and decide which polygon(s) to use as the "reference area" for the urban heat task.

**Sources**

- Venue names, zones and sports: every venue page on https://la28.org/en/games-plan/venues.html, scraped on 2026-11-23. The LA28 pages give **no addresses or coordinates**.
- Coordinates: geocoded with OpenStreetMap's Nominatim from each venue's real name (e.g. "DTLA Arena" = Crypto.com Arena, "2028 Stadium" = SoFi Stadium, "Exposition Park Stadium" = BMO Stadium, "Carson Stadium" = Dignity Health Sports Park). Many venues are temporary, so their points are approximate; see `location_note`.
- Polygons: Census TIGER/Line 2025 places (cities), counties and 2020 urban areas.
""")

code("""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import shape
from pystac_client import Client
import planetary_computer

pd.set_option('display.max_rows', 60)
pd.set_option('display.max_colwidth', 70)
""")

md("## All 49 venues")
code("""
venues = pd.read_csv('data/la28-venues.csv')
venues[['name', 'zone', 'sports', 'socal']]
""")

md("""
### Venues outside Southern California

Eight venues are elsewhere: six football (soccer) stadiums plus softball and canoe slalom in Oklahoma City. They are in other Landsat scenes and other climates, so they are out of scope for an LA heat analysis. That leaves **41 Southern California venues**.
""")
code("""
venues[~venues['socal']][['name', 'zone', 'sports']]
""")

md("## Southern California venues")
code("""
socal = venues[venues['socal']].copy()
socal = gpd.GeoDataFrame(socal,
                         geometry=gpd.points_from_xy(socal['lon'], socal['lat']),
                         crs='epsg:4326')

print('Venues:', len(socal))
print('Distinct locations:', socal.geometry.nunique())
""")

md("""
Several venues share one point: the three LA Convention Center halls, the four Valley Complexes (Sepulveda Basin), three Carson venues (Dignity Health Sports Park) and three Long Beach Convention Center venues. For a heat analysis these should be **one location each**, or they get counted several times.

How precise each point is:
""")
code("""
socal[['name', 'location_note', 'osm_match']]
""")

md("""
Venues to double-check on a map: Allianz Beach Arena (LA28 only says "westernmost edge of the coastline, next to downtown"), the Port of Los Angeles (sailing on open water: a land point doesn't represent it), Trestles (a surf break), and the road-cycling starts at Griffith Observatory and the LA Zoo (the course is a line, not a point).
""")

md("## Which cities and counties?")
code("""
places = gpd.read_file('data/tl_2025_06_place.zip').to_crs('epsg:4326')
counties = gpd.read_file('data/tl_2025_us_county.zip')
counties = counties[counties['STATEFP'] == '06'].to_crs('epsg:4326')

socal = (socal
         .sjoin(places[['NAME', 'geometry']].rename(columns={'NAME': 'city'}), how='left')
         .drop(columns='index_right')
         .sjoin(counties[['NAME', 'geometry']].rename(columns={'NAME': 'county'}), how='left')
         .drop(columns='index_right'))
socal['city'] = socal['city'].fillna('(unincorporated)')

socal[['name', 'zone', 'city', 'county']]
""")
code("""
socal.groupby(['county', 'city']).size().rename('n_venues').reset_index()
""")

md("""
**Summary:** 19 of 41 venues are in the City of Los Angeles. The rest are in 8 other cities (Long Beach, Carson, Inglewood, Pasadena, Arcadia, Pomona, Industry, Anaheim), two unincorporated parts of LA County (Universal City, Whittier Narrows) and Trestles, in unincorporated San Diego County. Anaheim is in Orange County.
""")

md("## Landsat coverage")
code("""
catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                      modifier=planetary_computer.sign_inplace)
items = catalog.search(collections=['landsat-c2-l2'],
                       bbox=list(socal.total_bounds),
                       datetime='2026-08-21/2026-08-22').item_collection()

footprints = gpd.GeoDataFrame({'id': [i.id for i in items]},
                              geometry=[shape(i.geometry) for i in items],
                              crs='epsg:4326')
footprints['n_venues'] = [socal.within(g).sum() for g in footprints.geometry]
footprints[['id', 'n_venues']]
""")

md("""
One scene (path 041, row 036) covers 40 of the 41 venues: everything except Trestles State Beach. Adding Trestles would mean merging two scenes, from two different days, which we haven't covered in class.
""")

md("## Map: venues, host cities and counties")
code("""
host_cities = places[places['NAME'].isin(socal['city'])]
socal_counties = counties[counties['NAME'].isin(['Los Angeles', 'Orange', 'San Diego'])]

fig, ax = plt.subplots(figsize=(10, 9))
socal_counties.to_crs(3857).boundary.plot(ax=ax, color='black', linewidth=1)
host_cities.to_crs(3857).plot(ax=ax, color='tab:orange', alpha=0.35, edgecolor='tab:orange')
footprints.to_crs(3857).boundary.plot(ax=ax, color='tab:blue', linestyle='--', linewidth=1)
socal.to_crs(3857).plot(ax=ax, color='red', markersize=20, zorder=3)

xmin, ymin, xmax, ymax = socal.to_crs(3857).total_bounds
ax.set_xlim(xmin - 20000, xmax + 20000)
ax.set_ylim(ymin - 15000, ymax + 15000)
ctx.add_basemap(ax, crs='epsg:3857', source=ctx.providers.Esri.WorldStreetMap, attribution_size=6)
ax.set_title('LA28 Southern California venues (red), host cities (orange),\\n'
             'counties (black) and Landsat scenes (blue dashes)')
ax.set_axis_off()
plt.show()
""")

md("""
## Options for the reference polygon

The heat task compares the surface temperature around venues to a reference area. Choices:

| Option | Polygons | Venues covered | Pros | Cons |
|---|---|---|---|---|
| A. City of Los Angeles only | 1 | 19 of 41 | Simplest; matches the current scratch notebook | Leaves out more than half the venues; TIGER boundary includes ocean |
| B. Each venue's host city | 9 cities + unincorporated areas | 38 of 41 (no polygon for the 3 unincorporated) | "Is this venue hotter than its own city?" is a fair local comparison | 9+ polygons and a loop; small cities give noisy averages; unincorporated venues need another rule |
| C. LA County | 1 | 39 of 41 (not Anaheim or Trestles) | One polygon | Includes mountains, Mojave Desert, and Catalina and San Clemente islands: not a fair comparison for urban venues; only 88% of it is in the Landsat scene |
| D. Census urban area "Los Angeles–Long Beach–Anaheim" | 1 | 38 of 41 | One polygon; the Census defines it as built-up land, which is exactly what we want to compare to; includes Anaheim; 99% inside one Landsat scene | Excludes Griffith Park (so Griffith Observatory and the LA Zoo fall outside) and Trestles; a less familiar dataset for students |
""")

code("""
urban = gpd.read_file('data/tl_2025_us_uac20.zip')
urban = urban[urban['NAME20'] == 'Los Angeles--Long Beach--Anaheim, CA'].to_crs('epsg:4326')

socal['in_urban_area'] = socal.within(urban.geometry.iloc[0])
print('Venues inside the urban area:', socal['in_urban_area'].sum(), 'of', len(socal))
socal.loc[~socal['in_urban_area'], ['name', 'city', 'county']]
""")

code("""
fig, ax = plt.subplots(figsize=(10, 8))
urban.to_crs(3857).plot(ax=ax, color='tab:purple', alpha=0.3, edgecolor='tab:purple')
socal[socal['in_urban_area']].to_crs(3857).plot(ax=ax, color='red', markersize=20, zorder=3)
socal[~socal['in_urban_area']].to_crs(3857).plot(ax=ax, color='black', marker='x', markersize=40, zorder=3)
footprints[footprints['id'].str.contains('041036')].to_crs(3857).boundary.plot(ax=ax, color='tab:blue', linestyle='--')

xmin, ymin, xmax, ymax = urban.to_crs(3857).total_bounds
ax.set_xlim(xmin - 10000, xmax + 10000)
ax.set_ylim(ymin - 40000, ymax + 10000)
ctx.add_basemap(ax, crs='epsg:3857', source=ctx.providers.Esri.WorldStreetMap, attribution_size=6)
ax.set_title('Census urban area Los Angeles–Long Beach–Anaheim (purple)\\n'
             'venues inside (red) and outside (black x); Landsat scene 041/036 (blue dashes)')
ax.set_axis_off()
plt.show()
""")

md("""
## Recommendation

**Option D, the Census urban area**, with this justification for students:

> *We want to know whether the ground around venues is hotter than the urban region the Games take place in. The Census urban area is the official boundary of continuously built-up land, so its average temperature represents "the city" as people experience it, without mountains, desert or ocean pulling the average down.*

Scope rules that come with it:

1. Keep the 38 venues inside the urban area, with shared locations merged into one point each.
2. Leave out Trestles (another scene, another county) and the road-cycling starts in Griffith Park (they're in parkland, and the event is a course, not a venue). Students can be told this or asked to find it.
3. Treat the Port of Los Angeles and Belmont Shore (water events) with care, or drop them: the heat question is about spectators on land.

Option B is a richer student exercise ("hotter than its own city?") but adds a loop over 9 cities and a rule for unincorporated areas, which goes against keeping it simple.
""")

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3 (ipykernel)', 'language': 'python'}
nbf.write(nb, HERE / 'la28-venues-polygons.ipynb')
print('Wrote', HERE / 'la28-venues-polygons.ipynb')

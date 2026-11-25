# Week 10: Parquet and GeoParquet lesson (draft handoff)

Written 2026-11-25. Draft lesson: `book/chapters/lesson-19-parquet/_lesson-19-parquet.qmd` (title "20 Parquet and GeoParquet").

## Status

- Draft only. The leading `_` keeps Quarto from rendering it. It is not in the sidebar in `_quarto.yml` and not on the week 10 page.
- To publish: install `pyarrow` in the environment that renders the site and add it to `eds220-env.yml`, rename the file to `lesson-19-parquet.qmd`, add it to the `book` sidebar in `_quarto.yml`, render the page, and commit the source, `_freeze/` and `docs/` together.
- Figures: the seven PNG files in `book/images/lesson-19/` are made by `_make-figures.py` in this folder (matplotlib only). To change a figure, edit the script and run it.
- The YAML has `lightbox: true`, so a figure opens enlarged when clicked. No other lesson uses it. Remove the line to turn it off.
- `references/references.bib` has six new entries for this lesson: `nysdec_spill_incidents_2026`, `us_census_bureau_tiger_2026_counties`, `apache_parquet`, `geoparquet`, `apache_arrow`, `overture_maps`.

## Needs a decision before class

1. **`pyarrow` is not in the course environment.** Neither `eds220-env.yml` nor the environment students built from commit `d3ce49f` has it, and `pd.read_parquet()` / `to_parquet()` fail without it. The lesson has a setup callout with `conda install -c conda-forge pyarrow`. This should be class preparation, not an in-class step. It also needs to be added to the workbench kernel.
2. **Data.** The lesson reuses the assignment 3 data: the spills CSV and the `tl_2026_us_county` folder. Students copy them from their `eds220-hwk3/data` folder. Decide whether to also put both on the course Drive.
3. **Spills file name.** The notes use `Spill_Incidents_20261030.csv`. Students' files have their own download date in the name.

## What was tested

- All code cells run without errors with pandas 2.3.3 and Python 3.12 in two setups: geopandas 1.1.4 as in `eds220-env.yml` with pyarrow 24.0.0 installed separately, and geopandas 0.14.4 (the version students have) with pyarrow 17.0.0. The second setup used the `pyogrio` engine to read and write shapefiles. Students have `fiona`, which was not tested.
- Not tested: the exact student environment (Python 3.11.4, numpy 1.24.3, pandas 2.3.2), which `pyarrow` version conda installs into it, Windows, and the workbench.
- The newest `pyarrow` from pip (26.0.1) fails to import with numpy 1.26.4. Versions 24.0.0 and 17.0.0 import fine.

## Length

The lesson is long for one 75-minute class. If time is short, the "Column names" subsection and Exercise 1 can move to the discussion section or stay as practice after class.

## Choices made

- The lesson does not use `bbox=` in `gpd.read_parquet()` or `write_covering_bbox=True`. Both need geopandas 1.0 or later, and students have 0.14.4. Region selection uses `filters` on the state code instead.
- `Spill Number` and `SWIS Code` are read as strings: both have leading zeros (SWIS codes start with 0 in about 10% of the rows).
- The lesson writes these files into `data/`: `spills_clean.csv` (104 MB), `spills.parquet` (23 MB), `counties.parquet` (126 MB), `ny_counties.parquet` and the `ny_counties` shapefile.

# Data pitfall catalog

The checklist for `data-literacy-review`. Each pitfall has a short description, the question that exposes it, and where it may appear in EDS 220. "Course examples" are leads to check against the data, not confirmed facts, unless marked confirmed. Add new pitfalls under the right type as they come up.

## Tabular

**Unit of observation.** It's unclear what one row represents (a survey, a site-year, an individual, an aggregate).
- Ask: "What does one row mean? Could two rows describe the same thing?"
- Course examples: bird species richness per wetland and year (L3: pandas subsetting, L4: plotting with pandas); hares (L18: linear regression, DS3).

**Effort and reporting bias.** Counts depend on how hard someone looked or who chose to report.
- Ask: "Does this count the thing, or the looking?"
- Course examples: bird richness depends on survey effort; salmon catch 1878–1997 reflects fishing effort and regulation, not abundance (HW2); NY spills are *reported* spills (HW3).

**Index vs. measurement.** A unitless or relative index gets treated like a physical quantity.
- Ask: "What is this number made of? Can you average it?"
- Course examples: AQI uses the worst pollutant of the day (HW2); EJI is a percentile rank relative to other tracts (DS8).

**Codes and categories defined only in the metadata.** Numeric or abbreviated codes are meaningless, or misleading, without the metadata.
- Ask: "Where is this code defined? Does `read_csv` read it as a number?"
- Course examples: hares `age` codes (L18, DS3); Arctic communities' country codes (L12: merging data).

**Categories or methods that change over time.** Definitions, instruments or methods change partway through a record.
- Ask: "Was this measured the same way the whole time?"
- Course examples: earthquake magnitude types (ml, mb, mw) that aren't directly comparable (HW1, DS5); Saffir-Simpson categories before and after satellites (DS4).

## Time series

**Fill values.** Sentinel values (`999.99`, `-9999`, `0`) are treated as data.
- Ask: "Is any value suspiciously round or extreme? What does the metadata say missing looks like?"
- Course examples: `HPCP` 999.99 in Boulder precipitation (L7: time series, confirmed and handled in the lesson).

**Missing vs. zero.** Missing periods are absent rather than coded, and resampling then treats them as zero or ignores them.
- Ask: "If nothing happened, is there a row?"
- Course examples: dry hours in the hourly precipitation data (L7).

**Timestamp conventions.** Hour-ending vs. hour-beginning, local time vs. UTC, and daylight saving time shift values across day boundaries.
- Ask: "What moment does this timestamp refer to?"
- Course examples: hour-ending convention in the Boulder data (L7, confirmed in the lesson's data description).

**Detection bias over time.** A record gets more complete over time and creates a false trend.
- Ask: "Is this an increase, or better detection?"
- Course examples: hurricanes (DS4), earthquakes (HW1, DS5).

**Aggregation hides or creates patterns.** The choice of resampling frequency and statistic (sum vs. mean vs. max) changes the story.
- Ask: "Would a different window or statistic tell a different story?"

## Point data

**Presence-only records.** An absence of points gets read as an absence of the thing.
- Ask: "Where could this be but nobody looked?"
- Course examples: wild pig occurrences (L10: geopandas intro).

**CRS not stored with the data.** A CSV with coordinates has no CRS, so a wrong guess fails silently.
- Ask: "How do we know the CRS? What happens if we guess wrong?"
- Course examples: power plants CSV, where the CRS (NAD83, EPSG:4269) appears only in the file name (L11: CSV to GeoDataFrame).

**Coordinate meaning and precision.** A point may be a facility, a town centroid or a geocoded address, and coordinate precision can be falsely high.
- Ask: "What exactly is at this point, and how precisely?"
- Course examples: approximate Arctic community locations (L12, DS6).

## Vector

**Scale and generalization.** Simplified boundaries drop small islands and move coastlines, so points fall outside every polygon.
- Ask: "At what map scale was this drawn? What disappears?"
- Course examples: Natural Earth 1:50m countries and populated places (L12, L13: clipping, DS6).

**Whose boundaries.** Boundaries are choices: disputed borders, territories included or not, and the year they were drawn.
- Ask: "Who drew this line, and when?"
- Course examples: Natural Earth's de facto borders; TIGER states that include territories (L13).

**Joins and clips drop features silently.** Inner joins, `sjoin` and `clip` remove features without warning.
- Ask: "How many rows before and after? Which ones disappeared, and why?"
- Course examples: L12, L13, DS6.

**Mapped products, not ground truth.** Perimeters and polygons come from different mapping methods, and their interiors may not be uniform.
- Ask: "How was this outline made? Is everything inside it the same?"
- Course examples: CALFIRE perimeters with unburned islands (L17: raster wrangling, HW4); different perimeter sources for the same fire (DS8).

**Aggregation units (MAUP).** Results depend on the units chosen, and units change over time.
- Ask: "Would the pattern hold with different boundaries?"
- Course examples: EJI by census tract (DS8).

## Raster and multi-dimensional

**Stored values aren't physical values.** Scale factors, offsets, integer storage and digital numbers vs. reflectance.
- Ask: "What does the metadata say to do to these numbers before using them?"
- Course examples: Landsat Collection 2 Level-2 scale and offset (HW4); NAIP 8-bit values, not atmospherically corrected (L15: rioxarray).

**Nodata and masks.** A nodata value (often 0) is included in statistics, or QA and cloud bands are ignored.
- Ask: "Which pixels should we not trust?"
- Course examples: Landsat nodata and QA pixel band (HW4).

**Model vs. measurement.** Classifications and models carry error but look like observations.
- Ask: "Is this observed, or modeled? How accurate is it?"
- Course examples: Copernicus DEM is a surface model that includes trees and buildings (L16: STAC); GAP/LANDFIRE is a classification (L17).

**Temporal mismatch.** Layers from different dates are combined as if they were simultaneous.
- Ask: "When was each layer made?"
- Course examples: 2011 land cover overlaid on 2017 fires (L17); NAIP mosaic tiles from different flight dates (L15).

**Resolution vs. the question.** The pixel size is too coarse for the question, or coarsening hides detail.
- Ask: "What's the smallest thing this data can see?"
- Course examples: 30 m land cover, 90 m DEM (L16, L17); coarsened Landsat in HW4 (Thomas fire version).

**Categorical rasters.** Averaging or bilinear resampling of class codes produces meaningless values.
- Ask: "Is this number a quantity or a label?"
- Course examples: GAP/LANDFIRE classes (L17).

**Metadata as provenance.** STAC properties (platform, date, processing level, license) are skipped.
- Ask: "What does the catalog tell us about how this was made?"
- Course examples: L16, L17, HW4.

## Across all types

**Simplified or derived copies.** The course version of a dataset differs from the original, and students don't know what was lost.
- Ask: "What did the course version leave out, and would it change our answer?"
- Course examples: bird richness (L3, L4), earthquakes (HW1, DS5), salmon (HW2), Landsat (HW4).

**Silent changes from code.** `dropna`, default inner merges, `astype`, NaN handling in groupby/resample, reprojection and resampling.
- Ask: "What did this line just do to the data?"

**Fitness for purpose.** The data is valid, but not for this question (wrong scale, time, population or variable).
- Ask: "Was this data collected to answer our question? If not, what's the gap?"

**Missing context about people and places.** Who is represented, who collected the data, and whose knowledge is left out.
- Ask: "Who is in this data, who isn't, and who decided?"
- Course examples: Arctic communities data from the Alaska Native Tribal Health Consortium (L12, DS6); EJI (DS8).

"""
Prepare the EIA power plants data for lesson 12 (Streamline your code).

Input: CSV of the "Power Plants in the US" layer downloaded from the EIA
U.S. Energy Atlas (https://atlas.eia.gov/datasets/eia::power-plants/about).
Its `Plant Longitude` and `Plant Latitude` columns are in WGS84 (EPSG:4326).

Output: data/power_plants_epsg4269.csv, with the coordinates in NAD83
(EPSG:4269) and the short column names the lesson uses.

Run from anywhere with the eds220-env environment active:
    python lesson-11-data-preparation.py
"""

from pathlib import Path

import pandas as pd
import geopandas as gpd

DATA_DIR = Path(__file__).parent / 'data'
INPUT_FP = DATA_DIR / 'Power_Plants_in_the_US_8679974854337621495.csv'
OUTPUT_FP = DATA_DIR / 'power_plants_epsg4269.csv'

# Short column names, matching the previous version of the lesson's CSV
COLUMN_NAMES = {
    'Object ID': 'objectid',
    'Energy Information Administration (EIA) Power Plant Identification Number': 'plant_code',
    'Electric Power Plant Name': 'plant_name',
    'Energy Information Administration (EIA) Utility Identifier': 'utility_id',
    'Operating Utility Name': 'utility_name',
    'Electric Power Sector': 'sector_name',
    'Plant Street Address': 'street_address',
    'Plant City Location': 'city',
    'Plant County Location': 'county',
    'Plant State Location': 'state',
    'Plant ZIP Code': 'zip',
    'Primary Energy Source': 'primsource',
    'Energy Source Description': 'source_desc',
    'Generation Technology Description': 'tech_desc',
    'Installed Nameplate Capacity (Megawatts)': 'install_mw',
    'Maximum Summer Capacity (Megawatts)': 'total_mw',
    'Battery Storage Capacity (Megawatts)': 'bat_mw',
    'Biomass Generation Capacity (Megawatts)': 'bio_mw',
    'Coal-Fired Generation Capacity (Megawatts)': 'coal_mw',
    'Geothermal Generation Capacity (Megawatts)': 'geo_mw',
    'Hydroelectric Generation Capacity (Megawatts)': 'hydro_mw',
    'Pumped Storage Hydroelectric Capacity (Megawatts)': 'hydrops_mw',
    'Natural Gas Generation Capacity (Megawatts)': 'ng_mw',
    'Nuclear Generation Capacity (Megawatts)': 'nuclear_mw',
    'Petroleum-Fired Generation Capacity (Megawatts)': 'crude_mw',
    'Solar Generation Capacity (Megawatts)': 'solar_mw',
    'Wind Generation Capacity (Megawatts)': 'wind_mw',
    'Other Generation Capacity (Megawatts)': 'other_mw',
    'Energy Information Administration (EIA) Data Source Surveys': 'source',
    'Data Reporting Period': 'period',
    'Plant Longitude': 'longitude',
    'Plant Latitude': 'latitude',
}

# The download starts with a byte order mark, hence utf-8-sig
power_plants = pd.read_csv(INPUT_FP, encoding='utf-8-sig')
n_rows = len(power_plants)

# Remove stray carriage returns (Windows line endings and a few utility names)
power_plants.columns = power_plants.columns.str.strip()
for column in power_plants.select_dtypes('object').columns:
    power_plants[column] = power_plants[column].str.strip('\r\n ')

# Keep the lesson's columns: drops the internal feature ID and the
# Web Mercator x and y columns
power_plants = power_plants[list(COLUMN_NAMES)].rename(columns=COLUMN_NAMES)

# Reproject the coordinates from WGS84 to NAD83
points = gpd.points_from_xy(power_plants['longitude'], power_plants['latitude'])
power_plants = gpd.GeoDataFrame(power_plants, geometry=points, crs='EPSG:4326')
power_plants = power_plants.to_crs('EPSG:4269')

# Replace the coordinate columns with the reprojected ones (6 decimals is ~0.1 m)
power_plants['longitude'] = power_plants.geometry.x.round(6)
power_plants['latitude'] = power_plants.geometry.y.round(6)
power_plants = pd.DataFrame(power_plants.drop(columns='geometry'))

# Check no rows or coordinates were lost
assert len(power_plants) == n_rows
assert power_plants[['longitude', 'latitude']].notna().all().all()

# Without the index, so the lesson doesn't need to drop an unnamed column
power_plants.to_csv(OUTPUT_FP, index=False)
print(f"Saved {len(power_plants)} power plants to {OUTPUT_FP}")

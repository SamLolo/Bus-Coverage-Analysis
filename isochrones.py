import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import r5py
import time
import pandas as pd
import geopandas as gpd
from data import DATA_DIR, TEMP_DIR, get_osm_extract
from datetime import datetime, timedelta

BATCH_SIZE = 100
MSOAID = "E02004156"

# Load MSOAs
msoas = gpd.read_file(DATA_DIR / "raw" / "Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_-6267947188164534400.gpkg", use_arrow=True)

# Convert to Lat/Long CRS to match centriods CRS
msoas.to_crs("EPSG:4326", inplace=True)
EXETER = msoas[msoas['MSOA21CD'] == MSOAID]

# Get all LSOA centriods in England
centriods = gpd.read_file(DATA_DIR / "processed" / "LSOA_Centres.gpkg", use_arrow=True)

# Find centriods that lie inside the region boundary using a spatial join
lsoas = centriods.sjoin(EXETER, how="inner")
lsoas.reset_index(inplace=True)
print(lsoas)

start_time = time.time()

get_osm_extract(MSOAID, lsoas, 70000)

print(f"Cropped OSM: {round(time.time() - start_time, 2)}s")
start_time = time.time()

# Create transport network for England
transport_network = r5py.TransportNetwork(
    osm_pbf = TEMP_DIR / f'{MSOAID}.osm.pbf',
    gtfs = [DATA_DIR / ".." / "poc" / "data" / "itm_south_west_gtfs.zip"]
)

print(f"Generated transport network: {round(time.time() - start_time, 2)}s")
start_time = time.time()

isochrones = []
for index, lsoa in lsoas.iterrows():

    bus = r5py.Isochrones(
        transport_network,
        origins=lsoa['geometry'],
        departure=datetime(2026, 1, 19, 8, 30),
        departure_time_window=timedelta(hours=1),
        transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        point_grid_resolution=100,
        isochrones=[40]
    )
    
    bus['id'] = lsoa['id']
    isochrones.append(bus.copy())

buses = pd.concat(isochrones)
buses.drop("travel_time", axis=1, inplace=True)

print(f"Created {lsoas.shape[0]} isochrones: {round(time.time() - start_time, 2)}s")
print(buses)
import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import r5py
import time
import subprocess
import pandas as pd
import geopandas as gpd
from pathlib import Path
from pyproj import Transformer
from shapely.ops import transform
from datetime import datetime, timedelta

PATH = Path(__file__).parent
TEMP_DIR = Path(__file__).parent.parent / "temp"

if not(os.path.exists(TEMP_DIR)):
    os.mkdir(TEMP_DIR)

MSOAID = "E02004156"

def get_osm_extract(id: str, gdf: gpd.GeoDataFrame, radius: float):
    dissolved_geometry = gdf.dissolve().at[0, 'geometry']
    
    to_meters = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    to_degrees = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

    dissolved_geometry = transform(to_meters, dissolved_geometry)
    buffered = dissolved_geometry.buffer(radius)
    dissolved_geometry = transform(to_degrees, buffered)
    
    min_long, min_lat, max_long, max_lat = dissolved_geometry.bounds

    cmd = [
        "osmium", "extract",
        "--bbox", f"{min_long},{min_lat},{max_long},{max_lat}",
        PATH / "data" / "england-260119.osm.pbf",
        "-o", TEMP_DIR / f"{id}.osm.pbf",
        "--overwrite",
    ]

    subprocess.run(cmd, check=True)

# Load MSOAs
msoas = gpd.read_file(PATH / "data" / "Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_-6267947188164534400.gpkg", use_arrow=True)

# Convert to Lat/Long CRS to match centriods CRS
msoas.to_crs("EPSG:4326", inplace=True)
EXETER = msoas[msoas['MSOA21CD'] == MSOAID]

# Get all LSOA centriods in England
centriods = gpd.read_file(PATH / "data" / "LSOA_Centres.gpkg", use_arrow=True)

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
    gtfs = [PATH / "data" / "itm_south_west_gtfs.zip"]
)

print(f"Generated transport network: {round(time.time() - start_time, 2)}s")
start_time = time.time()

isochrones = {
    "bus": [],
    "car": []
}
for index, lsoa in lsoas.iterrows():

    bus = r5py.Isochrones(
        transport_network,
        origins=lsoa['geometry'],
        departure=datetime(2026, 1, 19, 8, 30),
        departure_time_window=timedelta(hours=1),
        transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        point_grid_resolution=250,
        percentiles=[25],
        isochrones=[40]
    )
    
    bus['id'] = lsoa['id']
    isochrones['bus'].append(bus.copy())
    
    car = r5py.Isochrones(
        transport_network,
        origins=lsoa['geometry'],
        departure=datetime(2026, 1, 19, 8, 30),
        departure_time_window=timedelta(hours=1),
        transport_modes=[r5py.TransportMode.CAR],
        point_grid_resolution=500,
        isochrones=[40]
    )
    
    car['id'] = lsoa['id']
    isochrones['car'].append(car.copy())

buses = pd.concat(isochrones['bus'])
buses.drop("travel_time", axis=1, inplace=True)

cars = pd.concat(isochrones['car'])
cars.drop("travel_time", axis=1, inplace=True)

print(f"Created {lsoas.shape[0] * 2} isochrones: {round(time.time() - start_time, 2)}s")
print(buses)
print(cars)
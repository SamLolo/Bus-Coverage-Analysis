import os
import pyproj
import platform

os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

# Change AppData folder to avoid issues with file access permissions on windows
#if platform.system() == "Windows":
#    os.environ["LOCALAPPDATA"] = "C:/"
    
import r5py

import time
import geopandas as gpd
from data import DATA_DIR, TEMP_DIR, get_osm_extract
from datetime import datetime, timedelta
from poc.spatial_join import get_devon_lsoas

BATCH_SIZE = 100

# Load centriods
centriods = get_devon_lsoas()
centriods.reset_index(inplace=True)
origin = centriods.loc[0]
print(origin)
lat = origin['geometry'].y
long = origin['geometry'].x
print(lat, long)

start_time = time.time()

get_osm_extract(origin['id'], origin['geometry'].x, origin['geometry'].y, 70000)

print(f"Cropped OSM: {round(time.time() - start_time, 2)}s")
start_time = time.time()

# Create transport network for England
transport_network = r5py.TransportNetwork(
    osm_pbf = TEMP_DIR / f'{origin['id']}.osm.pbf',
    gtfs = [DATA_DIR / ".." / "poc" / "data" / "itm_south_west_gtfs.zip"]
)

print(f"Generated transport network: {round(time.time() - start_time, 2)}s")
start_time = time.time()

bus = r5py.Isochrones(
    transport_network,
    origins=origin['geometry'],
    departure=datetime(2026, 1, 19, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    point_grid_resolution=100,
    isochrones=[40]
)

print(f"Created isochrone: {round(time.time() - start_time, 2)}s")

print(bus)
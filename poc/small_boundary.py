import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import r5py
import time
import datetime
import geopandas as gpd
from pathlib import Path
from datetime import timedelta

# Set resolution
RESOLUTION_BUS = 250
RESOLUTION_CAR = 500

# Define Paths
PATH = Path(__file__).parent
OSM = PATH / "data" / "devon-260114.osm.pbf"
GTFS = PATH / "data" / "itm_south_west_gtfs.zip"
SAVE_BUS = PATH / "out" / f"exeter_bus_{RESOLUTION_BUS}.gpkg"
SAVE_CAR = PATH / "out"/ f"exeter_car_{RESOLUTION_CAR}.gpkg"

# Define LSOAs
EXE_CENTRE = "E01034630"
DEVON_BOUNDARY = "E01020046"
EXE1 = [f"E010346{x}" for x in range(20, 36)]
EXE2 = [f"E010{x}" for x in range(19968, 20041)]
DEVON1 = [f"E010202{x}" for x in range(0, 71)]

# Choose LSOAs (uncomment the one to use)
LSOAS = [EXE_CENTRE]
#LSOAS = [DEVON_BOUNDARY]
#LSOAS = EXE1 + EXE2 + DEVON1


#--------Load Centriods--------#


# Load processed centriods geopackage
start_time = time.time()
centriods = gpd.read_file(PATH / "data" / "LSOA_Centres.gpkg", use_arrow=True)

# Get GeoDataframe of chosen LSOAs
origins = centriods.loc[centriods['id'].isin(LSOAS)]
print(f"Loaded centriods: {round(time.time() - start_time, 2)} seconds")


#--------Create Transport Network--------#

# Transport network is slow to create first time but reads from memory 
# if the same network has been created before.

start_time = time.time()
transport_network = r5py.TransportNetwork(
    osm_pbf = OSM,
    gtfs = [GTFS]
)

print(f"Created transport network: {round(time.time() - start_time, 0)} seconds")


#--------Calculate Bus Isochrone(s)--------#


start_time = time.time()

buses = r5py.Isochrones(
    transport_network,
    origins=origins,
    departure=datetime.datetime(2026, 1, 19, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    percentiles=[25],
    point_grid_resolution=RESOLUTION_BUS,
    isochrones=[40]
)

print(f"Calculated {len(LSOAS)} isochrones: {round(time.time() - start_time, 0)} seconds")

# Save isochrones to file
buses["travel_time"] = buses["travel_time"].dt.total_seconds() / 60
buses.to_file(SAVE_BUS, driver="GPKG")


#--------Calculate Car Isochrone(s)--------#


start_time = time.time()

cars = r5py.Isochrones(
    transport_network,
    origins=origins,
    departure=datetime.datetime(2026, 1, 19, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.CAR],
    point_grid_resolution=RESOLUTION_CAR,
    isochrones=[40]
)

print(f"Calculated {len(LSOAS)} isochrones: {round(time.time() - start_time, 0)} seconds")

# Save isochrones to file
cars["travel_time"] = cars["travel_time"].dt.total_seconds() / 60
cars.to_file(SAVE_CAR, driver="GPKG")
import r5py
import time
import datetime
import geopandas as gpd
from pathlib import Path
from datetime import timedelta

DATA_DIR = Path(__file__).parent / '../data'

# Define Test LSOAS
EXETER_LSOA = "E01034630"
SECOND_LSOA = "E01000001"


#--------Load Centriods--------#


# Load processed centriods geopackage
start_time = time.time()
centriods = gpd.read_file(DATA_DIR / 'processed/LSOA_Centres.gpkg', use_arrow=True)

# Get Shapely point of test LSOAs
origin = centriods.loc[centriods['id'] == EXETER_LSOA, "geometry"].values[0]
origin2 = centriods.loc[centriods['id'] == SECOND_LSOA, "geometry"].values[0]

print(f"Loaded centriods: {round(time.time() - start_time, 2)} seconds")


#--------Create Transport Network--------#


# Create transport network for England
start_time = time.time()
transport_network = r5py.TransportNetwork(
    osm_pbf = DATA_DIR / "raw/england-260119.osm.pbf",
    gtfs = [DATA_DIR / "processed/england_gtfs_clean.zip"]
)

print(f"Created transport network: {round(time.time() - start_time, 0)} seconds")


#-------Calculate a bus isochrone--------#

# Calculate a single isochrone with the desired paramaters

start_time = time.time()

isochrones = r5py.Isochrones(
    
    transport_network,
    origins=origin,
    departure=datetime.datetime(2026, 1, 13, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    point_grid_resolution=200,
    isochrones=[40],
    max_time_walking=timedelta(minutes=20)
)

print(f"Calculated 1 isochrone (first-time): {round(time.time() - start_time, 0)} seconds")
print(isochrones)


#-------Caculate a second isochrone--------#

# This tests if there is any difference in computation time between 
# the first isochrone calculation and the second.

start_time = time.time()

isochrone2 = r5py.Isochrones(
    transport_network,
    origins=origin2,
    departure=datetime.datetime(2026, 1, 13, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    point_grid_resolution=200,
    isochrones=[40],
    max_time_walking=timedelta(minutes=20)
)

print(f"Calculated 1 isochrone (second-time): {round(time.time() - start_time, 0)} seconds")
print(isochrone2)
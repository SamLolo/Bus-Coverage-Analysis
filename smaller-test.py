import r5py
import time
import datetime
import geopandas as gpd
from datetime import timedelta

start_time = time.time()

EXE_CENTRE = ["E01034630"]
DEVON_BOUNDARY = ["E01020046"]
EXE1 = [f"E010346{x}" for x in range(20, 30)]
EXE2 = [f"E010346{x}" for x in range(31, 36)]
EXE3 = [f"E010{x}" for x in range(19968, 20041)]
DEVON1 = [f"E010202{x}" for x in range(0, 71)]
LSOAS = EXE_CENTRE

centriods = gpd.read_file("data/processed/LSOA_Centres.gpkg", use_arrow=True)
origins = centriods.loc[centriods['id'].isin(LSOAS)]

print(f"Loaded centriods: {round(time.time() - start_time, 2)} seconds")
start_time = time.time()

transport_network = r5py.TransportNetwork(
    osm_pbf = "data/raw/devon-260114.osm.pbf",
    gtfs = ["data/raw/itm_south_west_gtfs.zip"]
)

print(f"Created transport network: {round(time.time() - start_time, 0)} seconds")
start_time = time.time()

buses = r5py.Isochrones(
    transport_network,
    origins=origins,
    departure=datetime.datetime(2026, 1, 19, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    point_grid_resolution=100,
    isochrones=[40]
)

print(f"Calculated {len(LSOAS)} isochrones: {round(time.time() - start_time, 0)} seconds")

buses["travel_time"] = buses["travel_time"].dt.total_seconds() / 60
buses.to_file("out/exeter_bus.gpkg", driver="GPKG")

start_time = time.time()

cars = r5py.Isochrones(
    transport_network,
    origins=origins,
    departure=datetime.datetime(2026, 1, 19, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.CAR],
    point_grid_resolution=100,
    isochrones=[40]
)

print(f"Calculated {len(LSOAS)} isochrones: {round(time.time() - start_time, 0)} seconds")

cars["travel_time"] = cars["travel_time"].dt.total_seconds() / 60
cars.to_file("out/exeter_car.gpkg", driver="GPKG")
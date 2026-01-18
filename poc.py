import sys
sys.argv.append(["--max-memory", "16G"])
import r5py

import time
import datetime
import geopandas as gpd
from datetime import timedelta

start_time = time.time()

EXETER_LSOA = "E01034630"

SECOND_LSOA = "E01000001"

centriods = gpd.read_file("data/processed/LSOA_Centres.gpkg", use_arrow=True)
origin = centriods.loc[centriods['id'] == EXETER_LSOA, "geometry"].values[0]
origin2 = centriods.loc[centriods['id'] == SECOND_LSOA, "geometry"].values[0]

print(f"Loaded centriods: {round(time.time() - start_time, 2)} seconds")
start_time = time.time()

transport_network = r5py.TransportNetwork(
    osm_pbf = "data/raw/united-kingdom-260107.osm.pbf",
    gtfs = ["data/processed/england_gtfs_clean.zip"]
)

print(f"Created transport network: {round(time.time() - start_time, 0)} seconds")
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
isochrones["travel_time"] = isochrones["travel_time"].dt.total_seconds() / 60
isochrones.to_file("out/exeter.gpkg", driver="GPKG")


start_time = time.time()

iso2 = r5py.Isochrones(
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

print(iso2)


start_time = time.time()

# NOT WORKING!
iso_multi = r5py.Isochrones(
    transport_network,
    origins=centriods.iloc[1:101],
    departure=datetime.datetime(2026, 1, 13, 8, 30),
    departure_time_window=timedelta(hours=1),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    point_grid_resolution=200,
    isochrones=[40],
    max_time_walking=timedelta(minutes=20)
)

print(f"Calculated 100 isochrones: {round(time.time() - start_time, 0)} seconds")

print(iso_multi)
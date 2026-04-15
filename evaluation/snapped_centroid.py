import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import r5py
import json
import shapely
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from common.config import CONFIG
from common.data import TEMP_DIR, OUT_DIR, ROOT_DIR, Datasets, load_dataset
from isochrones.calculations import create_osm_extract, get_gtfs_regions
from isochrones.concat import convert_to_poly

# Get isochrone specific config
CONFIG = CONFIG['isochrones']

# Load invalid LSOAs and all lsoa CENTRIODS
invalid = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg")
lsoas = load_dataset(Datasets.CENTRIODS)

# Merge invalid LSOAs with their centriods
invalid = pd.merge(lsoas, invalid, on="id", how="left")
invalid.drop(["index_x", "index_y", "geometry_y"], axis=1, inplace=True)
invalid.rename({"geometry_x": "geometry"}, axis=1, inplace=True)

# Set new out directory
OUT_DIR = OUT_DIR / "evaluation"
if not(OUT_DIR.exists()):
    OUT_DIR.mkdir()
    
# Remove previous results
if "snapped_centroid_results.txt" in os.listdir(OUT_DIR):
    os.remove(OUT_DIR / "snapped_centroid_results.txt")

# Iterate through targets
with open(ROOT_DIR / "evaluation" / "targets.json") as file:
    targets = json.load(file)

# Isolate each invalid lsoa
for target, params in targets.items():
    lsoa = invalid.loc[invalid['id'] == target]
    
    # Create snapped centroid
    centroid = shapely.Point(params['snapped_coords'][0], params['snapped_coords'][1])

    # Create transport network for MSOA bounding box
    create_osm_extract(target, lsoa, CONFIG['bbox_radius'])
    regions = get_gtfs_regions(lsoa, CONFIG['gtfs_distance'])
    transport_network = r5py.TransportNetwork(
        osm_pbf = TEMP_DIR / f'{target}.osm.pbf',
        gtfs = regions
    )
    
    # Calculate bus isochrone
    bus = r5py.Isochrones(
        transport_network,
        origins=centroid,
        departure=CONFIG['departure'],
        departure_time_window=timedelta(minutes=CONFIG['departure_window']),
        transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        point_grid_resolution=250,
        percentiles=[25],
        isochrones=[CONFIG['travel_time']]
    )

    # Calculate car isochrone
    car = r5py.Isochrones(
        transport_network,
        origins=centroid,
        departure=CONFIG['departure'],
        departure_time_window=timedelta(minutes=CONFIG['departure_window']),
        transport_modes=[r5py.TransportMode.CAR, r5py.TransportMode.WALK],
        point_grid_resolution=500,
        isochrones=[CONFIG['travel_time']]
    )
    
    # Check if isochrones are empty
    with open(OUT_DIR / "snapped_centroid_results.txt", "a") as out_file:
        out_file.write(f"Target LSOA: {target}\n----------------------\n")
        out_file.write(f"Bus No Result: {bus.shape[0] == 0}\n")
        out_file.write(f"Car No Result: {car.shape[0] == 0}\n")
        if bus.shape[0] == 0 or car.shape[0] == 0:
            out_file.write("\n")
            continue
        
    # Polygonise shapes
    bus['geometry'] = bus['geometry'].apply(convert_to_poly)
    car['geometry'] = car['geometry'].apply(convert_to_poly)
    
    # Check if area is null
    with open(OUT_DIR / "snapped_centroid_results.txt", "a") as out_file:
        out_file.write(f"Bus Isochrone Empty: {bus.loc[0, 'geometry'] == None}\n")
        out_file.write(f"Car Isochrone Empty: {car.loc[0, 'geometry'] == None}\n")
        if bus.loc[0, 'geometry'] == None or car.loc[0, 'geometry'] == None:
            out_file.write("\n")
            continue
        
    # Check if ratio is greather than 1
    ratio = bus.loc[0, 'geometry'].area / car.loc[0, 'geometry'].area
    with open(OUT_DIR / "snapped_centroid_results.txt", "a") as out_file:
        out_file.write(f"Invalid Area Ratio: {ratio > 1} ({ratio})\n\n")
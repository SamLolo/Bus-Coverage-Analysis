import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import gc
import sys
import r5py
import getopt
import logging
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from common.config import CONFIG, setup_logging
from .calculations import create_osm_extract, get_gtfs_regions
from common.data import TEMP_DIR, OUT_DIR, Datasets, load_dataset, count_files

# Setup environment
setup_logging()
logger = logging.getLogger('lsoas')
CONFIG = CONFIG['isochrones']

# Set file paths of combined isochrone files
BUS_FILE = OUT_DIR / "bus_isochrones_combined.gpkg"
CAR_FILE = OUT_DIR / "car_isochrones_combined.gpkg"

# Load expected LSOA dataset
lsoas = load_dataset(Datasets.CENTRIODS)
boundaries = load_dataset(Datasets.LSOA_BOUNDARIES)

# Merge names into LSOAs centriods
lsoas = pd.merge(lsoas, boundaries, on="id", how="left")
lsoas.drop(["index_x", "index_y", "ruc", "geometry_y"], axis=1, inplace=True)
lsoas.rename({"geometry_x": "geometry"}, axis=1, inplace=True)

# Define possible command line arguments
short_args = "i:m:r:t:v"
long_args = ["lsoa-ids=", "max-memory=", "r5-classpath=", "temporary-directory=", "verbose"]

# Read command line arguments for LSOA list
arguments, values = getopt.getopt(sys.argv[1:], short_args, long_args)
for arg, val in arguments:
    if arg in ("-i", "--lsoa-ids"):
        lsoa_list = val.split(",")
        logger.info(f"LSOA list specified = {lsoa_list}")

# If list supplied, isolate target rows from full dataframe
if "lsoa_list" in locals():
    missing_lsoas = lsoas[lsoas['id'].isin(lsoa_list)]
else:
    
    # Load combined isochrone files or exit if they don't get exist
    if BUS_FILE.exists():
        bus_isochrones = gpd.read_file(BUS_FILE, use_arrow=True)
        logger.info("Loaded bus isochrones file")
    else:
        logger.error(f"Missing expected file: {BUS_FILE}")
        print(f"Missing expected file: {BUS_FILE}. \nPlease run 'isochrones.concat' first.")
        exit()
    if CAR_FILE.exists():
        car_isochrones = gpd.read_file(CAR_FILE, use_arrow=True)
        logger.info("Loaded car isochrones file")
    else:
        logger.error(f"Missing expected file: {CAR_FILE}")
        print(f"Missing expected file: {CAR_FILE}. \nPlease run 'isochrones.concat' first.")
        exit()
        
    # If no input list, find missing lsoas from output file and use those
    missing_bus: gpd.GeoDataFrame = pd.concat([bus_isochrones, lsoas]).drop_duplicates("id", keep=False)
    missing_car: gpd.GeoDataFrame = pd.concat([car_isochrones, lsoas]).drop_duplicates("id", keep=False)
    missing_lsoas: gpd.GeoDataFrame = pd.concat([missing_bus, missing_car])
    missing_lsoas = missing_lsoas.drop_duplicates("id")
    logger.info(f"Isolated {missing_lsoas.shape[0]} missing LSOAs")

# Create save-file name using previous out-files
bus_files = count_files(OUT_DIR, "^bus_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$")
car_files = count_files(OUT_DIR, "^car_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$")
BUS_SAVE = OUT_DIR / f"bus_isochrones{'.' + str(bus_files) if bus_files != 0 else ''}.gpkg"
CAR_SAVE = OUT_DIR / f"car_isochrones{'.' + str(car_files) if car_files != 0 else ''}.gpkg"

# Create empty dataframes
bus_isochrones = gpd.GeoDataFrame()
car_isochrones = gpd.GeoDataFrame()

# Find centriods that lie inside the each MSOA
logger.debug(f"Selected {missing_lsoas.shape[0]} target MSOAs")
for index in missing_lsoas.index:
    lsoa = missing_lsoas.loc[[index]]
    logger.info(f"Current lsoa = {lsoa.at[index, 'id']}")

    # Create transport network for MSOA bounding box
    try:
        create_osm_extract(lsoa.at[index, 'id'], lsoa, CONFIG['bbox_radius'])
        regions = get_gtfs_regions(lsoa, CONFIG['gtfs_distance'])
        transport_network = r5py.TransportNetwork(
            osm_pbf = TEMP_DIR / f'{lsoa.at[index, 'id']}.osm.pbf',
            gtfs = regions
        )
        logger.info("Created transport network")
    except Exception:
        logger.exception("Unable to create transport network")
        logger.warning(f"Skipped MSOA '{lsoa.at[index, 'id']}'")
        continue

    # Calculate bus isochrone
    try:
        bus = r5py.Isochrones(
            transport_network,
            origins=lsoa.at[index, 'geometry'],
            departure=CONFIG['departure'],
            departure_time_window=timedelta(minutes=CONFIG['departure_window']),
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            point_grid_resolution=CONFIG('bus_grid_res'),
            percentiles=[CONFIG('bus_percentile')],
            isochrones=[CONFIG['travel_time']]
        )
        
        # Warn if isochrone is empty
        if bus.shape[0] == 0:
            logger.warning(f"Blank bus isochrone for LSOA {lsoa.at[index, 'id']}")
        
        # Update attributes
        bus['id'] = lsoa.at[index, 'id']
        bus['name'] = lsoa.at[index, 'name']
        bus.drop("travel_time", axis=1, inplace=True)
        bus_isochrones: gpd.GeoDataFrame = pd.concat([bus_isochrones, bus])
    
        # Calculate car isochrone
        car = r5py.Isochrones(
            transport_network,
            origins=lsoa.at[index, 'geometry'],
            departure=CONFIG['departure'],
            departure_time_window=timedelta(minutes=CONFIG['departure_window']),
            transport_modes=[r5py.TransportMode.CAR, r5py.TransportMode.WALK],
            point_grid_resolution=CONFIG('car_grid_res'),
            percentiles=[CONFIG('car_percentile')],
            isochrones=[CONFIG['travel_time']]
        )
        
        # Warn if isochrone is empty
        if car.shape[0] == 0:
            logger.warning(f"Blank car isochrone for LSOA {lsoa.at[index, 'id']}")
        
        # Update attributes
        car['id'] = lsoa.at[index, 'id']
        car['name'] = lsoa.at[index, 'name']
        car.drop("travel_time", axis=1, inplace=True)
        car_isochrones: gpd.GeoDataFrame = pd.concat([car_isochrones, car])
        
        logger.info(f"Calculated isochrones")
    
    # Handle exception during isochrone calculation
    except Exception:
        logger.exception("An error occured whilst calculating isochrones")
        logger.warning(f"Skipped LSOA '{lsoa.at[index, 'id']}'")
        continue
    
    # Clean up transport network
    del transport_network
    gc.collect()
    logger.debug("Cleaned up transport network")
        
# Save isochrones before program exists
bus_isochrones.to_file(BUS_SAVE, driver="GPKG", use_arrow=True, overwrite=True)
logger.info(f"Isochrones saved to {BUS_SAVE}")
car_isochrones.to_file(CAR_SAVE, driver="GPKG", use_arrow=True, overwrite=True)
logger.info(f"Isochrones saved to {CAR_SAVE}")
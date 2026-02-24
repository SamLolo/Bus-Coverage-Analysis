import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import gc
import r5py
import logging
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from common.config import CONFIG, setup_logging
from .calculations import create_osm_extract, get_gtfs_regions
from common.data import TEMP_DIR, OUT_DIR, Datasets, load_dataset, count_files

setup_logging()
logger = logging.getLogger('lsoas')
CONFIG = CONFIG['isochrones']

# Set file paths
BUS_FILE = OUT_DIR / "bus_isochrones_combined.gpkg"
CAR_FILE = OUT_DIR / "car_isochrones_combined.gpkg"

# Loaded combined file
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

# Load expected lsoa dataset
lsoas = load_dataset(Datasets.CENTRIODS)
boundaries = load_dataset(Datasets.LSOA_BOUNDARIES)

# Merge names into lsoas centriods
lsoas = pd.merge(lsoas, boundaries, on="id", how="left")
lsoas.drop(["index_x", "index_y", "ruc", "geometry_y"], axis=1, inplace=True)
lsoas.rename({"geometry_x": "geometry"}, axis=1, inplace=True)
print(lsoas)

# Find missing LSOAs
#missing_bus: gpd.GeoDataFrame = pd.concat([bus_isochrones, lsoas]).drop_duplicates("id", keep=False)
#missing_car: gpd.GeoDataFrame = pd.concat([car_isochrones, lsoas]).drop_duplicates("id", keep=False)
#missing_lsoas: gpd.GeoDataFrame = pd.concat([missing_bus, missing_car])
#missing_lsoas = missing_lsoas.drop_duplicates("id")
#print(missing_lsoas)
#logger.info(f"Isolated {missing_lsoas.shape[0]} missing LSOAs")

# Manually define LSOAs to re-calculate
missing_lsoas = lsoas[lsoas['id'].isin(["E01027452", "E01028883", "E01035670"])]

# Create save-file name using previous out-files
bus_files = count_files(OUT_DIR, "^bus_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$")
car_files = count_files(OUT_DIR, "^car_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$")
BUS_SAVE = OUT_DIR / f"bus_isochrones{'.' + str(bus_files) if bus_files != 0 else ''}.gpkg"
CAR_SAVE = OUT_DIR / f"car_isochrones{'.' + str(car_files) if car_files != 0 else ''}.gpkg"

# Create empty dataframes
bus_isochrones = gpd.GeoDataFrame()
car_isochrones = gpd.GeoDataFrame()

# Find centriods that lie inside the each MSOA
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

    # Create Bus Isochrones
    try:
        bus = r5py.Isochrones(
            transport_network,
            origins=lsoa.at[index, 'geometry'],
            departure=CONFIG['departure'],
            departure_time_window=timedelta(minutes=CONFIG['departure_window']),
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            point_grid_resolution=250,
            percentiles=[25],
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
    
        car = r5py.Isochrones(
            transport_network,
            origins=lsoa.at[index, 'geometry'],
            departure=CONFIG['departure'],
            departure_time_window=timedelta(minutes=CONFIG['departure_window']),
            transport_modes=[r5py.TransportMode.CAR, r5py.TransportMode.WALK],
            point_grid_resolution=500,
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
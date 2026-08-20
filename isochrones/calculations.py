import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import gc
import sys
import r5py
import getopt
import logging
import shapely
import subprocess
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from shapely.ops import transform
from common.data import TEMP_DIR, OUT_DIR, Datasets, GTFS, get_filepath, load_dataset, count_files
from common.config import CONFIG, setup_logging

# Get Isochrone specific config
CONFIG = CONFIG['isochrones']

# Setup logging
setup_logging()
logger = logging.getLogger("isochrones")


def get_buffered_geometry(gdf: gpd.GeoDataFrame, radius: float) -> shapely.Polygon:
    """
    Creates a Polygon at a given radius around a set of points, defined within a `GeoDataFrame`.
    This is known as buffering the geometry. The returned Polygon is drawn such that all points lie within
    `radius` metres of the boundary line.

    Args:
        gdf (gpd.GeoDataFrame): A `GeoDataFrame` containing all points the radius should encompass.
        radius (float): The distance in metres to draw out to from all points.

    Returns:
        shapely.Polygon: The buttered geometry, typically a `Polygon`.
    """
    # Create single geometry containing all points
    dissolved_geometry: shapely.Point = gdf.dissolve().at[0, 'geometry']
    
    # Define transformation functions to and from EPSG:3857, which is the 2D CRS used by OpenStreetMap
    to_meters = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    to_degrees = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

    # Create the buffered geometry
    dissolved_geometry = transform(to_meters, dissolved_geometry)
    buffered = dissolved_geometry.buffer(radius)
    buffered_geometry = transform(to_degrees, buffered)
    return buffered_geometry


def create_osm_extract(name: str, gdf: gpd.GeoDataFrame, radius: int) -> None:
    """
    Creates an extract of the UK-wide Open-Street-Map (OSM) .pbf file.
    This is in the form of a square radius around the points defined within the `GeoDataFrame`.
    Saves the file to the temporary directory, defined within the config.

    Args:
        name (str): The save-name of the extract, excluding the `.osm.pbf` file extension.
        gdf (gpd.GeoDataFrame): The set of `shapely.Points` to create a bounding box around.
        radius (int): The minimum distance from the boundary of the bounding box to any of the points within `gdf`.
    """
    # Get geometry bounds that encompass all points within the specified radius
    geometry = get_buffered_geometry(gdf, radius)
    min_long, min_lat, max_long, max_lat = geometry.bounds

    # Create extract using osmium.exe cmd tool
    cmd = [
        "osmium", "extract",
        "--bbox", f"{min_long},{min_lat},{max_long},{max_lat}",
        get_filepath(Datasets.OSM),
        "-o", TEMP_DIR / f"{name}.osm.pbf",
        "--overwrite",
    ]
    subprocess.run(cmd, check=True)
    logger.debug(f"Created bounding box of radius = {radius}")
    
    
def get_gtfs_regions(gdf: gpd.GeoDataFrame, distance: int) -> list:
    """
    Find all GTFS regions that lie within a given distance from the set of points specified within a `GeoDataFrame`.

    Args:
        gdf (gpd.GeoDataFrame): The set of `shapely.Points` to search from.
        distance (int): The distance away from all points within `gdf` to include.

    Returns:
        list: An array of `pathlib.Path` objects representing the absolute filepaths of all relevant GTFS files.
    """
    # Get geometry bounds that encompass all points within the specified radius.
    geometry = get_buffered_geometry(gdf, distance)
    boundary = gpd.GeoDataFrame({'type': ['buffered']}, geometry=[geometry], crs="EPSG:4326")
    
    # Carry out spatial join between buffered geometry and GTFS regions
    regions = load_dataset(Datasets.REGIONS)
    overlap = regions.sjoin(boundary, predicate="intersects")
    
    # Add each overlapping GTFS region filepath to an array
    gtfs = []
    for _, row in overlap.iterrows():
        gtfs.append(get_filepath(GTFS(row['name'])))
        logger.debug(f"Including {GTFS(row['name'])}")
    return gtfs


# Define possible command line args
if __name__ == "__main__":
    short_args = "i:ids:m:r:t:v"
    long_args = ["msoa-index=", "msoa-ids=", "max-memory=", "r5-classpath=", "temporary-directory=", "verbose"]
    
    # Get command line arguments
    arguments, values = getopt.getopt(sys.argv[1:], short_args, long_args)
    for arg, val in arguments:
        if arg in ("-i", "--msoa-index"):
            range = [int(n) for n in val.split(":")]
            logger.info(f"MSOA range specified = {range}")
            break
        elif arg in ("-ids", "--msoa-ids"):
            msoa_list = val.split(",")
            logger.info(f"Explicit MSOA list specified = {msoa_list}")
            break
    
    # Create save-file name using previous out-files
    bus_files = count_files(OUT_DIR, "^bus_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$")
    car_files = count_files(OUT_DIR, "^car_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$")
    BUS_SAVE = OUT_DIR / f"bus_isochrones{'.' + str(bus_files) if bus_files != 0 else ''}.gpkg"
    CAR_SAVE = OUT_DIR / f"car_isochrones{'.' + str(car_files) if car_files != 0 else ''}.gpkg"
    
    # Select target MSOA based on cmd parameter
    msoas = load_dataset(Datasets.MSOA_BOUNDARIES)
    if "range" in locals():
        if len(range) >= 2:
            targets = msoas.loc[range[0]:range[1]]
        else:
            targets = msoas.loc[[range[0]]]
    elif "msoa_list" in locals():
        targets = msoas[msoas['id'].isin(msoa_list)]
    else:
        targets = msoas
    logger.debug(f"Found {targets.shape[0]} target MSOAs")
    
    # Group LSOAs by which MSOA they lie in using a spatial join
    centriods = load_dataset(Datasets.CENTRIODS)
    centriods = centriods.sjoin(targets, how="inner")
    logger.debug("Completed spatial join on LSOA centroids")
    
    # Create empty dataframes
    bus_isochrones = gpd.GeoDataFrame()
    car_isochrones = gpd.GeoDataFrame()
    
    # Find centriods that lie inside the each MSOA
    for index, msoa in targets.iterrows():
        logger.info(f"Current Index = {index}")
        lsoas = centriods.loc[centriods["id_right"] == msoa['id']]

        # Create transport network for MSOA bounding box
        try:
            create_osm_extract(msoa['id'], lsoas, CONFIG['bbox_radius'])
            regions = get_gtfs_regions(lsoas, CONFIG['gtfs_distance'])
            transport_network = r5py.TransportNetwork(
                osm_pbf = TEMP_DIR / f'{msoa['id']}.osm.pbf',
                gtfs = regions
            )
            logger.info("Created transport network")
        except Exception:
            logger.exception("Unable to create transport network")
            logger.warning(f"Skipped MSOA '{msoa['id']}'")
            continue

        # Start by creating lists of isochrones for each LSOA within the MSOA
        try:
            temp_bus = []
            temp_car = []
            for _, lsoa in lsoas.iterrows():
                
                # Calculate bus isochrones
                bus = r5py.Isochrones(
                    transport_network,
                    origins=lsoa['geometry'],
                    departure=CONFIG['departure'],
                    departure_time_window=timedelta(minutes=CONFIG['departure_window']),
                    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
                    point_grid_resolution=CONFIG['bus_grid_res'],
                    percentiles=[CONFIG['bus_percentile']],
                    isochrones=[CONFIG['travel_time']]
                )
                
                # Warn if isochrone is empty
                if bus.shape[0] == 0:
                    logger.warning(f"Blank bus isochrone for LSOA {lsoa['id_left']}")
                
                # Update attributes
                bus['id'] = lsoa['id_left']
                bus['name'] = lsoa['name']
                bus.drop("travel_time", axis=1, inplace=True)
                temp_bus.append(bus)

                # Calculate car isochrones
                car = r5py.Isochrones(
                    transport_network,
                    origins=lsoa['geometry'],
                    departure=CONFIG['departure'],
                    departure_time_window=timedelta(minutes=CONFIG['departure_window']),
                    transport_modes=[r5py.TransportMode.CAR],
                    point_grid_resolution=CONFIG['car_grid_res'],
                    percentiles=[CONFIG['car_percentile']],
                    isochrones=[CONFIG['travel_time']]
                )
                
                # Warn if isochrone is empty
                if car.shape[0] == 0:
                    logger.warning(f"Blank car isochrone for LSOA {lsoa['id_left']}")
                
                # Update attributes
                car['id'] = lsoa['id_left']
                car['name'] = lsoa['name']
                car.drop("travel_time", axis=1, inplace=True)
                temp_car.append(car)
            
            logger.info(f"Calculated {len(temp_bus) + len(temp_car)} isochrones")
        
        # Handle exception during isochrone calculation
        except Exception:
            logger.exception("An error occured whilst calculating isochrones")
            logger.warning(f"Skipped MSOA '{msoa['id']}'")
            continue
        
        # Add to GeoDataframes
        bus_isochrones: gpd.GeoDataFrame = pd.concat([bus_isochrones] + temp_bus)
        car_isochrones: gpd.GeoDataFrame = pd.concat([car_isochrones] + temp_car)
        logger.debug("Added isochrones to global dataframes")
        
        # Clean up transport network
        del transport_network
        gc.collect()
        logger.debug("Cleaned up transport network")
    
        # Save based on frequency defined in config
        try:
            if index % CONFIG['save_index'] == 0:
                bus_isochrones.to_file(BUS_SAVE, driver="GPKG", use_arrow=True)
                logger.info(f"Isochrones saved to {BUS_SAVE}")
                car_isochrones.to_file(CAR_SAVE, driver="GPKG", use_arrow=True)
                logger.info(f"Isochrones saved to {CAR_SAVE}")
                
        # Handle error whilst saving
        except Exception:
            logger.exception("Unable to save isochrones to disk")
            
    # Complete final save before program exists
    bus_isochrones.to_file(BUS_SAVE, driver="GPKG", use_arrow=True)
    logger.info(f"Isochrones saved to {BUS_SAVE}")
    car_isochrones.to_file(CAR_SAVE, driver="GPKG", use_arrow=True)
    logger.info(f"Isochrones saved to {CAR_SAVE}")
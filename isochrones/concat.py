import re
import logging
import pandas as pd
import geopandas as gpd
from shapely import MultiLineString, MultiPolygon
from shapely.ops import unary_union, linemerge, polygonize
from common.data import OUT_DIR, load_dataset, Datasets
from common.config import setup_logging

setup_logging()
logger = logging.getLogger("concat")

POLYGONISE = True

def convert_to_poly(geometry: MultiLineString) -> MultiPolygon:
    # Dissolve geometries together
    merged = unary_union(geometry)
    
    # Clean up line ends
    if type(merged) == MultiLineString:
        merged = linemerge(merged)
    
    # Convert to polygons
    polygons = list(polygonize(merged))
    
    # Create single MultiPolygon from list of polygons
    if polygons is not None:
        return MultiPolygon(polygons)
    else:
        return None
    

SEARCH_DIRS = [OUT_DIR]
logger.info(f"Search directories: {SEARCH_DIRS}")

# Create empty GeoDataFrame
bus_isochrones = gpd.GeoDataFrame()
car_isochrones = gpd.GeoDataFrame()
logger.debug("Created empty GeoDataFrames")

# Itterate through all directories to search
while len(SEARCH_DIRS) > 0:
    logger.info(f"Searching {SEARCH_DIRS[0]}")
    
    # For each file in directory, check if it is a file or a directory
    for file in SEARCH_DIRS[0].iterdir():
        if file.is_file():
            
            # Append to GeoDataFrame based on regex match
            if re.match("^bus_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$", file.name) is not None:
                try:
                    to_add = gpd.read_file(file.absolute(), use_arrow=True)
                    logger.debug(f"Loaded file: {file.relative_to(OUT_DIR)}")
                    bus_isochrones = pd.concat([bus_isochrones, to_add])
                    logger.debug("Added to bus isochrones")
                except:
                    logger.warning(f"Unable to load file: {file.relative_to(OUT_DIR)}")
            elif re.match("^car_isochrones(?:\\.[0-9]{1,3})?\\.gpkg$", file.name) is not None:
                try:
                    to_add = gpd.read_file(file.absolute(), use_arrow=True)
                    logger.debug(f"Loaded file: {file.relative_to(OUT_DIR)}")
                    car_isochrones = pd.concat([car_isochrones, to_add])
                    logger.debug("Added to car isochrones")
                except:
                    logger.warning(f"Unable to load file: {file.relative_to(OUT_DIR)}")
                
        # Add sub-directories to search tree
        elif file.is_dir():
            SEARCH_DIRS.append(file)
            logger.info(f"Found new search directory: {file.relative_to(OUT_DIR)}")
    
    # Remove directory once exhausted
    SEARCH_DIRS.pop(0)
    
# Remove duplicates
bus_isochrones = bus_isochrones.drop_duplicates("id", keep="first")
car_isochrones = car_isochrones.drop_duplicates("id", keep="first")
logger.info("Dropped duplicates")

# Drop extra columns
bus_isochrones.drop("geom", axis=1, inplace=True, errors='ignore')
car_isochrones.drop("geom", axis=1, inplace=True, errors='ignore')

# Load expected lsoa dataset
lsoas = load_dataset(Datasets.CENTRIODS)

# Find missing LSOAs
missing_bus: gpd.GeoDataFrame = pd.concat([bus_isochrones, lsoas]).drop_duplicates("id", keep=False)
missing_car: gpd.GeoDataFrame = pd.concat([car_isochrones, lsoas]).drop_duplicates("id", keep=False)
missing_lsoas: gpd.GeoDataFrame = pd.concat([missing_bus, missing_car])
missing_lsoas = missing_lsoas.drop_duplicates("id")
logger.info(f"Isolated {missing_lsoas.shape[0]} missing LSOAs")

# Cleaned missing LSOAs from both datasets
bus_isochrones = bus_isochrones[~bus_isochrones['id'].isin(missing_lsoas['id'])]
car_isochrones = car_isochrones[~car_isochrones['id'].isin(missing_lsoas['id'])]
logger.info(f"Cleaned missing LSOAs")

# Polygonise using the boundaries
if POLYGONISE:
    bus_isochrones['geometry'] = bus_isochrones['geometry'].apply(convert_to_poly)
    logger.info(f"Converted bus ischrones to polygons")
    car_isochrones['geometry'] = car_isochrones['geometry'].apply(convert_to_poly)
    logger.info(f"Converted car ischrones to polygons")

# Save to file
bus_isochrones.to_file(OUT_DIR / "bus_isochrones_combined.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
car_isochrones.to_file(OUT_DIR / "car_isochrones_combined.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
logger.info("Saved isochrones to files")
import re
import logging
import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR

logger = logging.getLogger("concat")

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
            if re.match("^bus_isochrones(?:\\.[0-9]{1,2})?\\.gpkg$", file.name) is not None:
                try:
                    to_add = gpd.read_file(file.absolute(), use_arrow=True)
                    logger.debug(f"Loaded file: {file.relative_to(OUT_DIR)}")
                    bus_isochrones = pd.concat([bus_isochrones, to_add])
                    logger.debug("Added to bus isochrones")
                except:
                    logger.warning(f"Unable to load file: {file.relative_to(OUT_DIR)}")
            elif re.match("^car_isochrones(?:\\.[0-9]{1,2})?\\.gpkg$", file.name) is not None:
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
bus_isochrones.drop_duplicates("id", ignore_index=True, inplace=True)
car_isochrones.drop_duplicates("id", ignore_index=True, inplace=True)
logger.info("Dropped duplicates")

# Drop extra columns
bus_isochrones.drop("geom", axis=1, inplace=True, errors='ignore')
car_isochrones.drop("geom", axis=1, inplace=True, errors='ignore')

# Save to file
bus_isochrones.to_file(OUT_DIR / "bus_isochrones_combined.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
car_isochrones.to_file(OUT_DIR / "car_isochrones_combined.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
logger.info("Saved isochrones to files")
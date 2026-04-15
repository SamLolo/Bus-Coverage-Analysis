import re
import logging
import pandas as pd
import geopandas as gpd
from shapely import MultiLineString, MultiPolygon
from shapely.ops import unary_union, linemerge, polygonize
from common.data import OUT_DIR, load_dataset, Datasets
from common.config import setup_logging

def convert_to_poly(geometry: MultiLineString) -> MultiPolygon:
    """
    Converts a `MultiLineString` into multiple polygons by joining the lines together at their ends if they meet,
    and creating a single geometry. This allows for things like area of the shape to be calculated properly.

    Args:
        geometry (shapely.MultiLineString): The `MultiLineString` produced by r5py's isochrone calculation.

    Returns:
        shapely.MultiPolygon: A `MultiPolygon` representing the set of polygons needed to create the shape of the `MultiLineString`.
    """
    # Dissolve geometries together
    merged = unary_union(geometry)
    
    # Clean up line ends
    if type(merged) == MultiLineString:
        merged = linemerge(merged)
    
    # Convert to polygons
    polygons = list(polygonize(merged))
    
    # Create single MultiPolygon from list of polygons
    if polygons is not None and len(polygons) > 0:
        return MultiPolygon(polygons)
    else:
        logger.warning("Found invalid polygon geometry")
        return None


if __name__ == "__main__":

    # Start logging
    setup_logging()
    logger = logging.getLogger("concat")

    # Whether to convert the isochrones from MultiLineStrings to Polygons
    POLYGONISE = True

    # Define the initial directories to search
    # Any sub-directories will also be searched and don't need to be included here.
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

    # Add names to some LSOAs that are missing them
    to_fill = {
        "E01033728": "Greenwich 035",
        "E01032638": "Southwark 035",
        "E01034188": "Greenwich 040",
        "E01035490": "Wandsworth 010",
        "E01001919": "Hammersmith and Fulham 018",
        "E01033582": "Newham 041",
        "E01032775": "Tower Hamlets 031",
        "E01018849": "Cornwall 048"
    }
    for id, name in to_fill.items():
        bus_isochrones.loc[bus_isochrones['id'] == id, "name"] = name
        car_isochrones.loc[car_isochrones['id'] == id, "name"] = name

    # Load expected LSOA dataset
    lsoas = load_dataset(Datasets.CENTRIODS)

    # Find missing LSOAs
    missing_bus: gpd.GeoDataFrame = pd.concat([bus_isochrones, lsoas]).drop_duplicates("id", keep=False)
    missing_car: gpd.GeoDataFrame = pd.concat([car_isochrones, lsoas]).drop_duplicates("id", keep=False)

    # Add reason that LSOAs were removed
    missing_bus['reason'] = "Missing bus isochrone"
    missing_car['reason'] = "Missing car isochrone"

    # Concat missing LSOAs into single df
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
        
    # Find isochrones with null area
    invalid_bus = bus_isochrones[bus_isochrones['geometry'].isna()].copy()
    invalid_car = car_isochrones[car_isochrones['geometry'].isna()].copy()

    # Add reason that LSOAs were removed
    invalid_bus['reason'] = "Bus isochrone has null area"
    invalid_car['reason'] = "Car isochrone has null area"

    # Concat invalid isochrones into single df
    invalid_lsoas: gpd.GeoDataFrame = pd.concat([invalid_bus, invalid_car])
    invalid_lsoas = invalid_lsoas.drop_duplicates("id")
    logger.info(f"Removed {invalid_lsoas.shape[0]} isochrones will null area")

    # Cleaned invalid LSOAs from both datasets
    bus_isochrones = bus_isochrones[~bus_isochrones['id'].isin(invalid_lsoas['id'])]
    car_isochrones = car_isochrones[~car_isochrones['id'].isin(invalid_lsoas['id'])]
    logger.info(f"Cleaned missing LSOAs")

    # Save to file
    bus_isochrones.to_file(OUT_DIR / "bus_isochrones_combined.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
    car_isochrones.to_file(OUT_DIR / "car_isochrones_combined.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
    logger.info("Saved isochrones to files")

    # Save removed isochrones to file
    removed: gpd.GeoDataFrame = pd.concat([missing_lsoas, invalid_lsoas])
    removed.to_file(OUT_DIR / "invalid_lsoas.gpkg", driver="GPKG", use_arrow=True, overwrite=True)
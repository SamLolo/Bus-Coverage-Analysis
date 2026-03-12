import os
import re
import logging
from enum import Enum
import geopandas as gpd
from pathlib import Path
from .config import CONFIG

logger = logging.getLogger("data")

# Create PathLin objects representing important file paths
ROOT_DIR: Path = Path(__file__).parent.parent
OUT_DIR: Path = ROOT_DIR / CONFIG['out_dir']
TEMP_DIR: Path = ROOT_DIR / CONFIG['temp_dir']

# Create out directory if it doesn't exist
if not(os.path.exists(OUT_DIR)):
    os.mkdir(OUT_DIR)

# Create temp directory if it doesn't exist
if not(os.path.exists(TEMP_DIR)):
    os.mkdir(TEMP_DIR)


class GTFS(Enum):
    """
    Enum used to represent each of the GTFS files for regions in England.
    Use `get_filepath()` to get the true filepath.
    """
    EAST_ANGLIA   = "East of England"
    LONDON        = "London"
    NORTH_EAST    = "North East"
    NORTH_WEST    = "North West"
    SOUTH_EAST    = "South East"
    SOUTH_WEST    = "South West"
    EAST_MIDLANDS = "East Midlands"
    WEST_MIDLANDS = "West Midlands"
    YORKSHIRE     = "Yorkshire and The Humber"


class Datasets(Enum):
    """
    Enum used to repesent all possible datsets.
    Can be used with `get_filepath()` or `load_dataset()` to query the dataset.
    
    For GTFS files, use the `GTFS` class.
    """
    DESTINATIONS    = "destinations"
    LSOA_BOUNDARIES = "lsoa_boundaries"
    MSOA_BOUNDARIES = "msoa_boundaries"
    CENTRIODS       = "centriods"
    REGIONS         = "regions"
    RUC_DEF         = "ruc_defintions"
    OSM             = "england_osm"
    COUNTIES        = "counties"
    

def get_filepath(dataset: GTFS|Datasets) -> Path:
    """
    Helper function to get the absolute filepath of a dataset or GTFS file.
    Filepaths can be configured in the `config.toml` file.

    Args:
        dataset (GTFS | Datasets): The requested dataset as an Enum.

    Raises:
        ValueError: Un-supported input type. Must be one of `GTFS` or `Datasets`.

    Returns:
        pathlib.Path: A `Path` object containing the absolute path.
    """
    if type(dataset) == Datasets:
        logger.debug(f"Requested filename: {dataset}")
        return ROOT_DIR / CONFIG['datasets'][dataset.value]
    elif type(dataset) == GTFS:
        logger.debug(f"Requested filename: {dataset}")
        return ROOT_DIR / CONFIG['datasets']['gtfs'][str(dataset.name).lower()]
    else:
        logger.error(f"No such dataset {repr(dataset)} when getting filename")
        raise ValueError("Unsupported input type")
    

def load_dataset(dataset: Datasets) -> gpd.GeoDataFrame:
    """
    Helper function to load any of the GeoPackage datasets into a GeoDataFrame ready to work with.

    Args:
        dataset (Datasets): The requested dataset as an Enum.

    Raises:
        ValueError: `Datasets.RUC_DEF` and `Datasets.OSM` are not geopackages and cannot be loaded using this function.

    Returns:
        gpd.GeoDataFrame: A `GeoDataFrame` containing the dataset within the specified geopackage file.
    """
    if not(dataset.name in ["RUC_DEF", "OSM"]):
        file = get_filepath(dataset)
        gdf = gpd.read_file(file, use_arrow=True)
        logger.debug(f"Loaded {dataset} as GeoDataFrame")
        return gdf
    else:
        logger.error(f"Attemped to load {dataset} as GeoDataFrame")
        raise ValueError("Unsupported dataset")
    

def count_files(dir: Path, regx: str) -> int:
    """
    Helper function to count the files within a directory, based on a regular expression.

    Args:
        dir (pathlib.Path): The directory to search within.
        regx (str): The regex to match against when counting.

    Returns:
        int: The number of matching files.
    """
    count = 0
    for file in dir.iterdir():
        if re.match(regx, file.name) is not None:
            count +=1
    return count
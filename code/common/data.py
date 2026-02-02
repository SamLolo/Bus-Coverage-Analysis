import os
import re
import logging
from enum import Enum
import geopandas as gpd
from pathlib import Path
from .config import CONFIG

logger = logging.getLogger("data")

ROOT_DIR: Path = Path(__file__).parent.parent.parent
OUT_DIR: Path = ROOT_DIR / CONFIG['out_dir']
TEMP_DIR: Path = ROOT_DIR / CONFIG['temp_dir']

if not(os.path.exists(OUT_DIR)):
    os.mkdir(OUT_DIR)

if not(os.path.exists(TEMP_DIR)):
    os.mkdir(TEMP_DIR)


class GTFS(Enum):
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
    DESTINATIONS = "destinations"
    LSOA_BOUNDARIES = "lsoa_boundaries"
    MSOA_BOUNDARIES = "msoa_boundaries"
    CENTRIODS = "centriods"
    REGIONS = "regions"
    RUC_DEF = "ruc_defintions"
    OSM = "england_osm"
    

def get_filepath(dataset: GTFS|Datasets) -> Path:
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
    if not(dataset.name in ["RUC_DEF", "OSM"]):
        file = get_filepath(dataset)
        gdf = gpd.read_file(file, use_arrow=True)
        logger.debug(f"Loaded {dataset} as GeoDataFrame")
        return gdf
    else:
        logger.error(f"Attemped to load {dataset} as GeoDataFrame")
        raise ValueError("Unsupported dataset")
    

def count_files(dir: Path, regx: str):
    count = 0
    for file in dir.iterdir():
        if re.match(regx, file.name) is not None:
            count +=1
    return count
import os
from enum import Enum
import geopandas as gpd
from pathlib import Path
from config import CONFIG

OUT_DIR = Path(__file__).parent / CONFIG['out_dir']
TEMP_DIR = Path(__file__).parent / CONFIG['temp_dir']

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
    

def get_filepath(dataset: GTFS|Datasets):
    if type(dataset) == Datasets:
        return Path(CONFIG['datasets'][dataset.value]).absolute()
    elif type(dataset) == GTFS:
        return Path(CONFIG['datasets']['gtfs'][str(dataset.name).lower()]).absolute()
    else:
        raise ValueError("Unsupported input type.")
    

def load_dataset(dataset: Datasets):
    if not(dataset.name in ["RUC_DEF", "OSM"]):
        file = get_filepath(dataset)
        gdf = gpd.read_file(file)
        return gdf
    else:
        raise ValueError("Unsupported dataset.")


print(get_filepath(GTFS.YORKSHIRE))
print(get_filepath(Datasets.OSM))
print(load_dataset(Datasets.CENTRIODS))
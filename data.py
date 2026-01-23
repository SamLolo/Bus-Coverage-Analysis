import os
import geopandas as gpd
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
OUT_DIR = Path(__file__).parent / 'out'
TEMP_DIR = Path(__file__).parent / 'temp'

if not(os.path.exists(OUT_DIR)):
    os.mkdir(OUT_DIR)

if not(os.path.exists(TEMP_DIR)):
    os.mkdir(TEMP_DIR)
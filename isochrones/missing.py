import logging
import pandas as pd
import geopandas as gpd
from common.config import setup_logging
from common.data import OUT_DIR, load_dataset, Datasets

# Start logging
setup_logging()
logger = logging.getLogger('check')

# Set file paths of combined isochrone files
BUS_FILE = OUT_DIR / "bus_isochrones_combined.gpkg"
CAR_FILE = OUT_DIR / "car_isochrones_combined.gpkg"

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

# Load boundaries
lsoas = load_dataset(Datasets.CENTRIODS)
msoas = load_dataset(Datasets.MSOA_BOUNDARIES)

# Find missing LSOAs
missing_bus: gpd.GeoDataFrame = pd.concat([bus_isochrones, lsoas]).drop_duplicates("id", keep=False)
missing_car: gpd.GeoDataFrame = pd.concat([car_isochrones, lsoas]).drop_duplicates("id", keep=False)
logger.info("Isolated missing LSOAs")

# Join missing LSOAs with MSOA boundaries
bus_msoas = missing_bus.sjoin(msoas, how="inner")
car_msoas = missing_car.sjoin(msoas, how="inner")

# Isolate missing MSOA indicies across both dataframes
bus_indicies = list(bus_msoas.groupby('index_right').groups.keys())
car_indicies = list(car_msoas.groupby('index_right').groups.keys())
missing_indicies = list(set(bus_indicies + car_indicies))
missing_indicies.sort()
logger.info(f"Found {len(missing_indicies)} missing MSOAs")
logger.info(f"Missing: {missing_indicies}")

# Create group of individual indicies and df slices to re-calculate
indicies = []
current = [missing_indicies[0], missing_indicies[0]]
for index in missing_indicies:
    if index > current[1] + 1:
        if current[0] != current[1]:
            indicies.append(f"{current[0]}:{current[1]}")
        else:
            indicies.append(str(current[0]))
        current = [index, index]
    else:
        current[1] = index
        
# Add last index to list if not already present
if not(f"{current[0]}:{current[1]}" in indicies) or not(str(current[0]) in indicies):
    if current[0] != current[1]:
        indicies.append(f"{current[0]}:{current[1]}")
    else:
        indicies.append(str(current[0]))
logger.info("Created list of indicies and dataframe slices to re-calculate")

# Write output to text file
if len(indicies) > 0:
    with open(OUT_DIR / "missing.txt", "w") as file:
        file.write("\n".join(indicies))
        logger.info(f"Wrote output to file {OUT_DIR / 'missing.txt'}")
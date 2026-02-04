import logging
import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR, load_dataset, Datasets

logger = logging.getLogger('check')

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

# Load boundaries
lsoas = load_dataset(Datasets.CENTRIODS)
msoas = load_dataset(Datasets.MSOA_BOUNDARIES)

# Find missing LSOAs
missing_bus: gpd.GeoDataFrame = pd.concat([bus_isochrones, lsoas]).drop_duplicates("id", keep=False)
missing_car: gpd.GeoDataFrame = pd.concat([car_isochrones, lsoas]).drop_duplicates("id", keep=False)
logger.info("Isolated missing LSOAs")

# Choose dataframe with more missing rows to calculate
if missing_bus.shape[0] > missing_car.shape[0]:
    missing_df = missing_bus
else:
    missing_df = missing_car

# Join mssing lsoas with 
missing_msoas = msoas.sjoin(missing_df)
logger.info(f"Found {missing_msoas.groupby('index_left').ngroups} missing MSOAs")

# Isolate missing MSOA indicies
keys = list(missing_msoas.groupby('index_left').groups.keys())

# Create group of induvidual indicies and df slices to re-calculate
indicies = []
current = [keys[0], keys[0]]
for key in keys:
    if key > current[1] + 1:
        if current[0] != current[1]:
            indicies.append(f"{current[0]}:{current[1]}")
        else:
            indicies.append(str(current[0]))
        current = [key, key]
    else:
        current[1] = key
logger.info("Created list of indicies and dataframe slices to re-calculate")

# Write output to text file
with open(OUT_DIR / "missing.txt", "w") as file:
    file.write("\n".join(indicies))
    logger.info(f"Wrote output to file {OUT_DIR / 'missing.txt'}")
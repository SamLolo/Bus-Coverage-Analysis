import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR

# Define LSOA ID to plot
TARGET_LSOA = "E01027452"

# Load isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones.1.gpkg")
car = gpd.read_file(OUT_DIR / "car_isochrones.1.gpkg")

# Set type to serve as key on map
bus['type'] = "Bus + Walking"
car['type'] = "Driving"

# Combine isochrones into single dataframe
combined = pd.concat([bus, car])
combined = combined[combined['id'].str.contains(TARGET_LSOA)]
print(combined)

# Create interactive map and save as html file to explore
map = combined.explore(column="type", cmap=["blue", "purple"])
map.save(OUT_DIR / f"{TARGET_LSOA}_isochrones.html")
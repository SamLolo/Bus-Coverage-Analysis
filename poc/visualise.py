import pandas as pd
import geopandas as gpd
from pathlib import Path

PATH = Path(__file__).parent

# Load isochrones
bus = gpd.read_file(PATH / "out" / "exeter_bus.gpkg")
car = gpd.read_file(PATH / "out" / "exeter_car.gpkg")

# Set type to serve as key on map
bus['type'] = "Bus + Walking"
car['type'] = "Driving"

# Combine isochrones into single dataframe
combined = pd.concat([bus, car])
print(combined)

# Create interactive map and save as html file to explore
map = combined.explore(column="type", cmap=["blue", "purple"])
map.save(PATH / "out" / "exeter.html")
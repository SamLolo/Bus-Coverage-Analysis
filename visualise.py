import pandas as pd
import geopandas as gpd

bus = gpd.read_file("out/exeter_bus.gpkg")
car = gpd.read_file("out/exeter_car.gpkg")

bus['type'] = "Bus + Walking"
car['type'] = "Driving"

combined = pd.concat([bus, car])
print(combined)

map = combined.explore(column="type", cmap=["blue", "purple"])
map.save("out/exeter.html")
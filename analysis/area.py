import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR

# Load completed isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg", use_arrow=True)
car = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg", use_arrow=True)

# Convert to cylindrical equal-area format 
bus.to_crs({'proj':'cea'}, inplace=True) 
car.to_crs({'proj':'cea'}, inplace=True) 

# Combine df's on ID
area_df: gpd.GeoDataFrame = pd.merge(bus, car, on="id")

# Calculate area in square km's
area_df['bus_area'] = area_df['geometry_x'].area / 10**6
area_df['car_area'] = area_df['geometry_y'].area / 10**6

# Calculate ratio of bus to car area
area_df['ratio'] = (area_df['bus_area'] / area_df['car_area'])

# Clean up dataframe
area_df.rename({"name_x": "name"}, axis=1, inplace=True)
area_df.drop(["name_y", "geometry_x", "geometry_y"], axis=1, inplace=True)

# Save to file
area_df.to_csv(OUT_DIR / "areas.csv")
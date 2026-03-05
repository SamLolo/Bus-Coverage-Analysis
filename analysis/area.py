import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR

# Load completed isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg", use_arrow=True)
car = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg", use_arrow=True)
print("Loaded isochrones")

# Convert to cylindrical equal-area format 
bus_cea = bus.to_crs({'proj':'cea'}) 
car_cea = car.to_crs({'proj':'cea'})
print("Converted to cylindrical equal-area")

# Combine df's on ID
area_df: gpd.GeoDataFrame = pd.merge(bus_cea, car_cea, on="id")
print("Combined dataframes")

# Calculate area in square km's
area_df['bus_area'] = area_df['geometry_x'].area / 10**6
area_df['car_area'] = area_df['geometry_y'].area / 10**6
print("Calculated areas")

# Calculate ratio of bus to car area
area_df['ratio'] = (area_df['bus_area'] / area_df['car_area'])
print("Calculated ratio")

# Clean up dataframe
area_df.rename({"name_x": "name"}, axis=1, inplace=True)
area_df.drop(["name_y", "geometry_x", "geometry_y"], axis=1, inplace=True)
print("Cleaned dataframe")

# Remove lsoas with area ratios > 1 as these are considered invalid
outliers = area_df[area_df['ratio'] > 1].copy()
area_df = area_df[area_df['ratio'] <= 1]
outliers.to_csv(OUT_DIR / "area_outliers.csv")
print("Removed outliers and saved them to seperate file")

# Remove invalid lsoas from original combined isochrone files
invalid_ratios = bus[bus['id'].isin(outliers['id'])].copy()
bus = bus[~bus['id'].isin(invalid_ratios['id'])]
car = car[~car['id'].isin(invalid_ratios['id'])]
print("Removed lsoas with ratio > 1")

# Update invalid lsoas dataframe
invalid = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg")
invalid_ratios['reason'] = "Area ratio is greater than 1"
invalid = pd.concat([invalid, invalid_ratios])
print("Add removed lsoas to 'invalid_lsoas.gpkg'")

# Save to file
area_df.to_csv(OUT_DIR / "areas.csv")
bus.to_file(OUT_DIR / "bus_isochrones_combined.gpkg", driver="GPKG", use_arrow=True)
car.to_file(OUT_DIR / "car_isochrones_combined.gpkg", driver="GPKG", use_arrow=True)
invalid.to_file(OUT_DIR / "invalid_lsoas.gpkg", driver="GPKG", use_arrow=True)
print("Saved to files")
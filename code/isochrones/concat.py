import re
import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR

SEARCH_DIRS = [OUT_DIR / "Federico's Mac"]

# Create empty GeoDataFrame
bus_isochrones = gpd.GeoDataFrame()
car_isochrones = gpd.GeoDataFrame()

# Itterate through all directories to search
while len(SEARCH_DIRS) > 0:
    
    # For each file in directory, check if it is a file or a directory
    for file in SEARCH_DIRS[0].iterdir():
        if file.is_file():
            
            # Append to GeoDataFrame based on regex match
            if re.match("^bus_isochrones(?:\\.[0-9]{1,2})?\\.gpkg$", file.name) is not None:
                to_add = gpd.read_file(file.absolute(), use_arrow=True)
                bus_isochrones = pd.concat([bus_isochrones, to_add])
            elif re.match("^car_isochrones(?:\\.[0-9]{1,2})?\\.gpkg$", file.name) is not None:
                to_add = gpd.read_file(file.absolute(), use_arrow=True)
                car_isochrones = pd.concat([car_isochrones, to_add])
                
        # Add sub-directories to search tree
        elif file.is_dir():
            SEARCH_DIRS.append(file)
    
    # Remove directory once exhausted
    SEARCH_DIRS.pop(0)
    
# Remove duplicates
bus_isochrones.drop_duplicates("id", ignore_index=True, inplace=True)
car_isochrones.drop_duplicates("id", ignore_index=True, inplace=True)

# Save to file
bus_isochrones.to_file(OUT_DIR / "bus_isochrones_combined.gpkg", driver="GPKG", use_arrow=True)
car_isochrones.to_file(OUT_DIR / "car_isochrones_combined.gpkg", driver="GPKG", use_arrow=True)
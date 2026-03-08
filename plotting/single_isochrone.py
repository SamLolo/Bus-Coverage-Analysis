import pandas as pd
import geopandas as gpd
import contextily as cx
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Define LSOA id to plot
TARGET_LSOA = "E01034628"

# Load isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg")
car = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg")

# Load centriods
centriods = load_dataset(Datasets.CENTRIODS)

# Set type to serve as key on map
bus['type'] = "Bus + Walking"
car['type'] = "Driving"

# Combine isochrones into single dataframe
combined: gpd.GeoDataFrame = pd.concat([car, bus])

# Isolate target LSOA
combined = combined[combined['id'].str.contains(TARGET_LSOA)]
centriods = centriods[centriods['id'].str.contains(TARGET_LSOA)]

# Convert to Web Mercator CRS for plotting
combined.to_crs("EPSG:3857", inplace=True)
centriods.to_crs("EPSG:3857", inplace=True)

# Plot isochrones
ax = combined.plot(figsize=(10, 10), 
                   column="type", 
                   alpha=0.6, 
                   cmap="RdBu",
                   legend=True,
                   legend_kwds={
                       "loc": "upper left"
                   })

# Plot centriod
ax = centriods.plot(ax=ax, markersize=1, color="black")

# Add OSM basemap
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)

# Disable axis
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "exeter_isochrones.png", 
            dpi=600, 
            bbox_inches='tight', 
            pad_inches=0)
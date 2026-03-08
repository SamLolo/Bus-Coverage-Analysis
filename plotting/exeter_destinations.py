import geopandas as gpd
import contextily as cx
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Define LSOA id to plot
TARGET_LSOA = "E01034628"

# Load only bus isochrone for target LSOA
isochrones = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg")
isochrones = isochrones[isochrones['id'].str.contains(TARGET_LSOA)]

# Load destinations
destinations = load_dataset(Datasets.DESTINATIONS)

# Isolate select destinations within isochrone
destinations = destinations[destinations['type'].isin(["gp", "hospital", "primary_school", "secondary_school", "further_education"])]
destinations = destinations.sjoin(isochrones, predicate="intersects")

# Update names
destinations['type'] = destinations['type'].apply(lambda x: ' '.join(word.capitalize() for word in x.split("_")))

# Convert to Web Mercator CRS for plotting
isochrones.to_crs("EPSG:3857", inplace=True)
destinations.to_crs("EPSG:3857", inplace=True)

# Plot bus isochrone
ax = isochrones.plot(figsize=(10, 10),  
                     alpha=0.3, 
                     color="0.4")
ax = isochrones.boundary.plot(ax=ax,  
                              linewidth=0.6, 
                              color="black")

# Plot centriod
ax = destinations.plot(ax=ax,
                       column="type",
                       markersize=30, 
                       legend=True)

# Add OSM basemap
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)

# Disable axis
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "exeter_destinations.png", 
            dpi=600, 
            bbox_inches='tight', 
            pad_inches=0)
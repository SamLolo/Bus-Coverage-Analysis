import geopandas as gpd
import contextily as cx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from common.data import OUT_DIR, load_dataset, Datasets

# Define LSOA id to plot
TARGET_LSOA = "E01034628"

# Load only bus isochrone for target LSOA
isochrones = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg")
isochrones = isochrones[isochrones['id'].str.contains(TARGET_LSOA)]

# Load destinations and centiods
destinations = load_dataset(Datasets.DESTINATIONS)
centriods = load_dataset(Datasets.CENTRIODS)

# Isolate select destinations within isochrone
destinations = destinations[destinations['type'].isin(["gp", "hospital", "primary_school", "secondary_school", "further_education"])]
destinations = destinations.sjoin(isochrones, predicate="intersects")

# Update names
destinations['type'] = destinations['type'].apply(lambda x: ' '.join(word.capitalize() for word in x.split("_")))
destinations['type'] = destinations['type'].replace("Gp", "GP")

# Convert to Web Mercator CRS for plotting
isochrones.to_crs("EPSG:3857", inplace=True)
destinations.to_crs("EPSG:3857", inplace=True)
centriods.to_crs("EPSG:3857", inplace=True)

# Plot bus isochrone
ax = isochrones.plot(figsize=(10, 10),  
                     alpha=0.3, 
                     color="0.4")
ax = isochrones.boundary.plot(ax=ax,  
                              linewidth=0.6, 
                              color="black")

# Define custom colormap
colours = {
    "GP": "red",
    "Hospital": "brown",
    "Primary School": "green",
    "Secondary School": "purple",
    "Further Education": "blue"
}
cmap = ListedColormap([colours[name] for name in destinations['type'].unique()])

# Plot destinations
ax = destinations.plot(ax=ax,
                       column="type",
                       cmap=cmap,
                       markersize=35,
                       legend=True)

# Plot Isochrone Centriod
ax = centriods[centriods["id"] == TARGET_LSOA].plot(ax=ax,
                                                    marker="*",
                                                    markersize=75,
                                                    color="black")

# Add start point to legend
legend = ax.get_legend()
start_handle = Line2D([0], [0], color="white", marker='*', markerfacecolor='black', markersize=15)
ax.legend([start_handle] + legend.legend_handles, ["Isochrone Centre"] + [t.get_text() for t in legend.texts])

# Add OSM basemap
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)

# Disable axis
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "exeter_destinations.png", 
            dpi=600, 
            bbox_inches='tight', 
            pad_inches=0)
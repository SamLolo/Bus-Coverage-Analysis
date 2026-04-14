import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import r5py
import pandas as pd
import contextily as cx
import geopandas as gpd
from datetime import timedelta
import matplotlib.pyplot as plt
from common.config import CONFIG
from matplotlib.lines import Line2D
from common.data import TEMP_DIR, OUT_DIR, Datasets, load_dataset
from isochrones.calculations import create_osm_extract, get_gtfs_regions

# Get isochrone specific config
CONFIG = CONFIG['isochrones']

# Load invalid LSOAs
invalid = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg")

# Load other neccessary dataset
lsoas = load_dataset(Datasets.CENTRIODS)
destinations = load_dataset(Datasets.DESTINATIONS)
destinations.rename({"urn": "id"}, axis=1, inplace=True)

# Merge invalid LSOAs with their centriods
invalid = pd.merge(lsoas, invalid, on="id", how="left")
invalid.drop(["index_x", "index_y", "geometry_y"], axis=1, inplace=True)
invalid.rename({"geometry_x": "geometry"}, axis=1, inplace=True)

# Set target lsoa (Docklands, London)
TARGET = "E01034212"
lsoa = invalid.loc[invalid['id'] == TARGET]

# Set target destination (Newham Hospital)
destination = destinations.loc[destinations['id'] == "R1HNH"]

# Create transport network for MSOA bounding box
create_osm_extract(TARGET, lsoa, CONFIG['bbox_radius'])
regions = get_gtfs_regions(lsoa, CONFIG['gtfs_distance'])
transport_network = r5py.TransportNetwork(
    osm_pbf = TEMP_DIR / f'{TARGET}.osm.pbf',
    gtfs = regions
)

# Complete point-to-point travel calculation
routes = r5py.DetailedItineraries(
    transport_network,
    origins=lsoa,
    destinations=destination,
    departure=CONFIG['departure'],
    departure_time_window=timedelta(minutes=CONFIG['departure_window']),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
)
routes['mode'] = routes.transport_mode.astype(str).map({
    "TransportMode.BUS": "Bus",
    "TransportMode.WALK": "Walking"
})

# Filter by valid routes (under 40 minutes)
valid = {}
for option, route in routes.groupby("option", sort=False):
    time = route['travel_time'].sum() + route['wait_time'].sum()
    if time.total_seconds() <= 2400:
        valid[option] = time
        
# Sort by fastest time
valid = dict(sorted(valid.items(), key=lambda x: x[1]))
        
# Output results
print("\nRoute: E01034212 -> Newham Hospital")
print("Number of valid routes:", len(valid))
print(f"Quickest Route: {list(valid.values())[0]}\n")

# Create a map of the quickest route
quickest = routes[routes['option'] == list(valid.keys())[0]]
quickest = quickest.to_crs("EPSG:3857")
ax = quickest.plot(column="mode", legend=True)

# Add markers for origin and destination
lsoa = lsoa.to_crs("EPSG:3857")
ax = lsoa.plot(ax=ax, marker="s", markersize=20, color="black")
destination = destination.to_crs("EPSG:3857")
ax = destination.plot(ax=ax, marker="X", markersize=20, color="black")

# Update legend
legend = ax.get_legend()
start_handle = Line2D([0], [0], color="white", marker='s', markerfacecolor='black', markersize=10)
end_handle = Line2D([0], [0], color="white", marker='X', markerfacecolor='black', markersize=10)
ax.legend([start_handle, end_handle] + legend.legend_handles, ["Start", "End"] + [t.get_text() for t in legend.texts], fontsize=10, loc="upper left")

# Add OSM basemap
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, attribution_size=4)
plt.axis('off')
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "evaluation" / f"{TARGET}_point_to_point.png", 
            dpi=600, 
            bbox_inches='tight', 
            pad_inches=0)
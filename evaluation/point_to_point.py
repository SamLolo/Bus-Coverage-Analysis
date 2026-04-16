import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import r5py
import json
import pandas as pd
import contextily as cx
import geopandas as gpd
from datetime import timedelta
import matplotlib.pyplot as plt
from common.config import CONFIG
from matplotlib.lines import Line2D
from common.data import TEMP_DIR, OUT_DIR, ROOT_DIR, Datasets, load_dataset
from isochrones.calculations import create_osm_extract, get_gtfs_regions

# Get isochrone specific config
CONFIG = CONFIG['isochrones']

# Load invalid LSOAs
invalid = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg")

# Set new out directory
OUT_DIR = OUT_DIR / "evaluation"
if not(OUT_DIR.exists()):
    OUT_DIR.mkdir()
    
# Remove previous results
if "point_to_point_results.txt" in os.listdir(OUT_DIR):
    os.remove(OUT_DIR / "point_to_point_results.txt")

# Load other neccessary dataset
lsoas = load_dataset(Datasets.CENTRIODS)
destinations = load_dataset(Datasets.DESTINATIONS)
destinations.rename({"urn": "id"}, axis=1, inplace=True)

# Merge invalid LSOAs with their centriods
invalid = pd.merge(lsoas, invalid, on="id", how="left")
invalid.drop(["index_x", "index_y", "geometry_y"], axis=1, inplace=True)
invalid.rename({"geometry_x": "geometry"}, axis=1, inplace=True)

# Iterate through targets
with open(ROOT_DIR / "evaluation" / "targets.json") as file:
    targets = json.load(file)

# Isolate each invalid lsoa
for target, params in targets.items():
    lsoa = invalid.loc[invalid['id'] == target]

    # Set target destination
    destination = destinations.loc[destinations['id'] == params['destination']]

    # Create transport network for MSOA bounding box
    create_osm_extract(target, lsoa, CONFIG['bbox_radius'])
    regions = get_gtfs_regions(lsoa, CONFIG['gtfs_distance'])
    transport_network = r5py.TransportNetwork(
        osm_pbf = TEMP_DIR / f'{target}.osm.pbf',
        gtfs = regions
    )

    # Complete point-to-point travel calculation
    try:
        routes = r5py.DetailedItineraries(
            transport_network,
            origins=lsoa.iloc[[0]],
            destinations=destination.iloc[[0]],
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
                
        # Output results
        with open(OUT_DIR / "point_to_point_results.txt", "a") as out_file:
            out_file.write(f"\nRoute: {target} -> {destination.iat[0, 1]}\n")
            out_file.write(f"Number of valid routes: {len(valid)}\n")
                
        # Sort by fastest time
        if len(valid) > 0:
            valid = dict(sorted(valid.items(), key=lambda x: x[1]))
            with open(OUT_DIR / "point_to_point_results.txt", "a") as out_file:
                out_file.write(f"Quickest Route: {list(valid.values())[0]}\n")

            # Create a map of the quickest route
            quickest = routes[routes['option'] == list(valid.keys())[0]]
            quickest = quickest.to_crs("EPSG:3857")
            ax = quickest.plot(column="mode", legend=True)

            # Add markers for origin and destination
            lsoa = lsoa.to_crs("EPSG:3857")
            ax = lsoa.plot(ax=ax, marker="o", markersize=15, color="black")
            destination = destination.to_crs("EPSG:3857")
            ax = destination.plot(ax=ax, marker="X", markersize=15, color="black")

            # Update legend
            legend = ax.get_legend()
            start_handle = Line2D([0], [0], color="white", marker='o', markerfacecolor='black', markersize=10)
            end_handle = Line2D([0], [0], color="white", marker='X', markerfacecolor='black', markersize=10)
            ax.legend([start_handle, end_handle] + legend.legend_handles, ["Start", "End"] + [t.get_text() for t in legend.texts], fontsize=10, loc="upper left")

            # Add OSM basemap
            cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, attribution_size=4)
            plt.axis('off')
            plt.tight_layout()

            # Save to png
            PLOT_DIR = OUT_DIR / "plots"
            if not(PLOT_DIR.exists()):
                PLOT_DIR.mkdir()
            plt.savefig(PLOT_DIR / f"{target}_point_to_point.png", 
                        dpi=600, 
                        bbox_inches='tight', 
                        pad_inches=0)
    
    # Handle failed computations
    except Exception as ex:
        with open(OUT_DIR / "point_to_point_results.txt", "a") as out_file:
            out_file.write(f"\nRoute: {target} -> {destination.iat[0, 1]}\n")
            out_file.write(f"Computation failed ({type(ex)})\n")
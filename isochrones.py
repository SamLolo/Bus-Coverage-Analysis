import os
import pyproj

# Fix issue with pyproj not having correct env variables on conda
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import sys
import r5py
import getopt
import shapely
import subprocess
import pandas as pd
import geopandas as gpd
from shapely.ops import transform
from datetime import datetime, timedelta
from data import TEMP_DIR, OUT_DIR, Datasets, GTFS, get_filepath, load_dataset

from config import CONFIG
CONFIG = CONFIG['isochrones']


def get_buffered_geometry(gdf: gpd.GeoDataFrame, radius: float) -> shapely.geometry:
    dissolved_geometry = gdf.dissolve().at[0, 'geometry']
    
    to_meters = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    to_degrees = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

    dissolved_geometry = transform(to_meters, dissolved_geometry)
    buffered = dissolved_geometry.buffer(radius)
    dissolved_geometry = transform(to_degrees, buffered)
    
    return dissolved_geometry


def create_osm_extract(id: str, gdf: gpd.GeoDataFrame, radius: int) -> None:
    geometry = get_buffered_geometry(gdf, radius)
    
    min_long, min_lat, max_long, max_lat = geometry.bounds

    cmd = [
        "osmium", "extract",
        "--bbox", f"{min_long},{min_lat},{max_long},{max_lat}",
        get_filepath(Datasets.OSM),
        "-o", TEMP_DIR / f"{id}.osm.pbf",
        "--overwrite",
    ]
    subprocess.run(cmd, check=True)
    
    
def get_gtfs_regions(gdf: gpd.GeoDataFrame, distance: int):
    geometry = get_buffered_geometry(gdf, distance)
    boundary = gpd.GeoDataFrame({'type': ['buffered']}, geometry=[geometry], crs="EPSG:4326")
    
    regions = load_dataset(Datasets.REGIONS)
    overlap = regions.sjoin(boundary, predicate="intersects")
    
    gtfs = []
    for _, row in overlap.iterrows():
        gtfs.append(get_filepath(GTFS(row['name'])))
    return gtfs
    

if __name__ == "__main__":
    short_args = "i:m:r:t:v"
    long_args = ["msoa-index=", "max-memory=", "r5-classpath=", "temporary-directory=", "verbose"]
    
    # Get command line arguments
    arguments, values = getopt.getopt(sys.argv[1:], short_args, long_args)
    for arg, val in arguments:
        if arg in ("-i", "--msoa-index"):
            range = [int(n) for n in val.split(":")]
    
    # Select target MSOA based on cmd parameter
    msoas = load_dataset(Datasets.MSOA_BOUNDARIES)
    if "range" in locals():
        targets = msoas.loc[range[0]:range[1]]
    else:
        targets = msoas
    
    # Group LSOAs by which MSOA they lie in using a spatial join
    centriods = load_dataset(Datasets.CENTRIODS)
    centriods = centriods.sjoin(targets, how="inner")
    
    # Create empty dataframes
    bus_isochrones = gpd.GeoDataFrame()
    car_isochrones = gpd.GeoDataFrame()
    
    # Find centriods that lie inside the each MSOA
    for index, msoa in targets.iterrows():
        lsoas = centriods.loc[centriods["id_right"] == msoa['id']]

        # Create transport network for MSOA bounding box
        create_osm_extract(msoa['id'], lsoas, CONFIG['bbox_radius'])
        regions = get_gtfs_regions(lsoas, CONFIG['gtfs_distance'])
        transport_network = r5py.TransportNetwork(
            osm_pbf = TEMP_DIR / f'{msoa['id']}.osm.pbf',
            gtfs = regions
        )

        # Create Bus Isochrones
        isochrones = []
        for _, lsoa in lsoas.iterrows():
            bus = r5py.Isochrones(
                transport_network,
                origins=lsoa['geometry'],
                departure=CONFIG['departure'],
                departure_time_window=timedelta(minutes=CONFIG['departure_window']),
                transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
                point_grid_resolution=250,
                percentiles=[25],
                isochrones=[CONFIG['travel_time']]
            )
            
            # Update attributes
            bus['id'] = lsoa['id']
            bus['name'] = lsoa['name']
            bus.drop("travel_time", axis=1, inplace=True)
            isochrones.append(bus)
        
        # Add to Geodataframe
        bus_isochrones: gpd.GeoDataFrame = pd.concat(bus_isochrones + isochrones)
        
        # Create Car Isochrones
        isochrones = []
        for _, lsoa in lsoas.iterrows():
            car = r5py.Isochrones(
                transport_network,
                origins=lsoa['geometry'],
                departure=CONFIG['departure'],
                departure_time_window=timedelta(minutes=CONFIG['departure_window']),
                transport_modes=[r5py.TransportMode.CAR],
                point_grid_resolution=500,
                isochrones=[CONFIG['travel_time']]
            )
            
            # Update attributes
            car['id'] = lsoa['id']
            car['name'] = lsoa['name']
            car.drop("travel_time", axis=1, inplace=True)
            isochrones.append(car)
            
        # Add to Geodataframe
        car_isochrones: gpd.GeoDataFrame = pd.concat(car_isochrones + isochrones)
        
    print(bus_isochrones)
    print(car_isochrones)
    
    # Save based on frequency defined in config
    if index % CONFIG['save_index'] == 0:
        bus_isochrones.to_file(OUT_DIR / "bus_isochrones.gpkg", driver="GPKG", use_arrow=True)
        car_isochrones.to_file(OUT_DIR / "car_isochrones.gpkg", driver="GPKG", use_arrow=True)
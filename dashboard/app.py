from flask import Flask
import geopandas as gpd
from common.data import OUT_DIR, load_dataset, Datasets

class IsochroneApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.centroids = load_dataset(Datasets.CENTRIODS)
        self.bus_isochrones = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg", use_arrow=True)
        self.car_isochrones = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg", use_arrow=True)
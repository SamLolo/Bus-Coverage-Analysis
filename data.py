import subprocess
import geopandas as gpd
from pathlib import Path
from pyproj import Transformer
from shapely.ops import transform

DATA_DIR = Path(__file__).parent / 'data'
OUT_DIR = Path(__file__).parent / 'out'
TEMP_DIR = Path(__file__).parent / 'temp'

def get_osm_extract(id: str, gdf: gpd.GeoDataFrame, radius: float):
    dissolved_geometry = gdf.dissolve().at[0, 'geometry']
    
    to_meters = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    to_degrees = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

    dissolved_geometry = transform(to_meters, dissolved_geometry)
    buffered = dissolved_geometry.buffer(radius)
    dissolved_geometry = transform(to_degrees, buffered)
    
    min_long, min_lat, max_long, max_lat = dissolved_geometry.bounds

    cmd = [
        "osmium", "extract",
        "--bbox", f"{min_long},{min_lat},{max_long},{max_lat}",
        DATA_DIR / "raw" / "england-260119.osm.pbf",
        "-o", TEMP_DIR / f"{id}.osm.pbf",
        "--overwrite",
    ]

    subprocess.run(cmd, check=True)
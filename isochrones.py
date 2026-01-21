import r5py
import geopandas as gpd
from data import DATA_DIR

BATCH_SIZE = 1000

# Create transport network for England
transport_network = r5py.TransportNetwork(
    osm_pbf = DATA_DIR / "raw" / "england-260119.osm.pbf",
    gtfs = [DATA_DIR / "processed" / "england_gtfs_clean.zip"]
)
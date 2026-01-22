import math
import subprocess
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
OUT_DIR = Path(__file__).parent / 'out'
TEMP_DIR = Path(__file__).parent / 'temp'

def get_osm_extract(
    id: str,
    long: float,
    lat: float,
    radius: float,
):
    dlat = radius / 111_000
    dlon = radius / (111_000 * math.cos(math.radians(lat)))

    bbox = (
        long - dlon,
        lat - dlat,
        long + dlon,
        lat + dlat,
    )

    cmd = [
        "osmium", "extract",
        "--bbox", f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        DATA_DIR / "raw" / "england-260119.osm.pbf",
        "-o", TEMP_DIR / f"{id}.osm.pbf",
        "--overwrite",
    ]

    subprocess.run(cmd, check=True)
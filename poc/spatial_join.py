import geopandas as gpd
from pathlib import Path

PATH = Path(__file__).parent

"""
A simple function that returns the LSOAs that fall within the regional boundary of Devon.

Returns:
    geopandas.GeoDataFrame: The LSOA population-weighted centriods within Devon.
"""
def get_devon_lsoas():
    # Load regions
    regions = gpd.read_file(PATH / "data" / "ITL2_JAN_2025_UK_BUC_-4202672173330737482.gpkg", use_arrow=True)
    
    # Convert to Lat/Long CRS to match centriods CRS
    regions.to_crs("EPSG:4326", inplace=True)
    devon = regions[regions['ITL225CD'] == "TLK4"]

    # Get all LSOA centriods in England
    centriods = gpd.read_file(PATH / "data" / "LSOA_Centres.gpkg", use_arrow=True)

    # Find centriods that lie inside the region boundary using a spatial join
    lsoas = centriods.sjoin(devon, how="inner")
    return lsoas
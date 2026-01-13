import os 
import pandas as pd
import geopandas as gpd

PATH = os.path.dirname(os.path.realpath(__file__))


#--------Import Raw Datasets--------#


# LSOA Boundaries
print("Importing LSOA Boundaries...")
boundaries: gpd.GeoDataFrame = gpd.read_file(f'{PATH}/raw/Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4_6453788336260919790.gpkg', use_arrow=True)
print(f"Found {boundaries.shape[0]} Rows.\n")

# LSOA Centriods
print("Importing LSOA Centrioids...")
centres: gpd.GeoDataFrame = gpd.read_file(f'{PATH}/raw/LSOA_PopCentroids_EW_2021_V4_-3471144733095659889.gpkg', use_arrow=True)
print(f"Found {centres.shape[0]} Rows.\n")

# RUC classifications
print("Importing LSOA Classes...")
classes = pd.read_csv(f'{PATH}/raw/Rural_Urban_Classification_(2021)_of_LSOAs_in_EW.csv')
print(f"Found {classes.shape[0]} Rows.\n")

# Destinations
print("Importing Destination Dataset...")
sheets = pd.read_excel(f'{PATH}/raw/journey-time-statistics-2019-destination-datasets.ods', sheet_name=[1, 2, 3, 4, 5, 6, 7, 8], header=2)
print(f"Found {len(sheets.keys())} Sheets.\n")


#--------Process LSOAs--------#


# Remove Welsh LSOAs
boundaries = boundaries[~boundaries['LSOA21CD'].str.contains("W")]
classes = classes[~classes['LSOA21CD'].str.contains("W")]

# Concatenate RUC classifications
lsoas: gpd.GeoDataFrame = pd.merge(boundaries, classes, on='LSOA21CD', how="outer")

# Save RUC classification meanings seperately
ruc_def = pd.Series(classes['RUC21NM'].values, index = classes['RUC21CD'])
ruc_def.drop_duplicates(inplace=True)
ruc_def.to_json(f'{PATH}/processed/RUC_definitions.json', orient='index', indent=1)
print("Created RUC Definitions Dataset at 'processed/RUC_definitions.json'")

# Drop unwanted columns
lsoas.drop(["LSOA21NMW_x", "BNG_E", "BNG_N", "LAT", "LONG", "GlobalID", "LSOA21NM_y", "LSOA21NMW_y", "RUC21NM", "Urban_rural_flag", "ObjectId"], axis=1, inplace=True)
lsoas.rename({"LSOA21CD": "LSOACode", "LSOA21NM_x": "LSOAName", "RUC21CD": "RUCCode"}, axis=1, inplace=True)

# Save as a GeoPackage
lsoas.to_file(f'{PATH}/processed/LSOA_Boundaries.gpkg', driver="GPKG", use_arrow=True)
print("Updated LSOA Dataset with RUC classifcations at 'processed/LSOA_Boundaries.gpkg'")


#--------Process LSOA Centriods--------#


# Remove Welsh LSOAs
centres = centres[~centres['LSOA21CD'].str.contains("W")]

# Modify Columns
centres.drop(["GlobalID", "GlobalID_2"], axis=1, inplace=True)
centres.rename({"LSOA21CD": "LSOAName"}, axis=1, inplace=True)

# Change to Long/Lat Coords
centres.to_crs("EPSG:4326", inplace=True)

# Save to GeoPackage
centres.to_file(f'{PATH}/processed/LSOA_Centres.gpkg', driver="GPKG", use_arrow=True)
print("Updated LSOA Centriods Dataset at 'processed/LSOA_Centres.gpkg'")


#--------Process other destinations-----------#


# Remame fields in GP and Hospitals to match schools
sheets[1].rename({"LSOACode": "URN", "LSOAName": "EstablishmentName"}, axis=1, inplace=True)
sheets[2].rename({"LSOACode": "URN", "LSOAName": "EstablishmentName"}, axis=1, inplace=True)
sheets[3].rename({"LSOACode": "URN", "LSOAName": "EstablishmentName"}, axis=1, inplace=True)
sheets[7].rename({"GP_Code": "URN", "Postcode": "EstablishmentName"}, axis=1, inplace=True)
sheets[8].rename({"SiteCode": "URN", "SiteName": "EstablishmentName"}, axis=1, inplace=True)

# Annonate each dataframe with type of destination
sheets[1].insert(4, "Type", "Small Employment")
sheets[2].insert(4, "Type", "Medium Employment")
sheets[3].insert(4, "Type", "Large Employment")
sheets[4].insert(4, "Type", "Primary School")
sheets[5].insert(4, "Type", "Secondary School")
sheets[6].insert(4, "Type", "Further Education")
sheets[7].insert(4, "Type", "GP")
sheets[8].insert(4, "Type", "Hospital")

# Join sheets and sort by LSOA Code
dest_df = pd.concat([sheets[1], sheets[2], sheets[3], sheets[4], sheets[5], sheets[6], sheets[7], sheets[8]])

# Convert column datatypes
dest_df['URN'] = dest_df['URN'].astype(str)
dest_df['EstablishmentName'] = dest_df['EstablishmentName'].astype(str)
dest_df['Type'] = dest_df['Type'].astype(str)

# Convert to GeoDataframe with Lat/Long Coords
dest_gdf = gpd.GeoDataFrame(dest_df, geometry=gpd.points_from_xy(dest_df['Easting'], dest_df['Northing']), crs="EPSG:27700")
dest_gdf.to_crs("EPSG:4326", inplace=True)

# Save as a GeoPackage
dest_gdf.to_file(f'{PATH}/processed/Destinations.gpkg', driver="GPKG", use_arrow=True)
print("Updated Destinations Dataset at 'processed/Destinations.gpkg'")
import os 
import pandas as pd
import geopandas as gpd

PATH = os.path.dirname(os.path.realpath(__file__))


#--------Import LSOA Boundaries--------#


print("Importing LSOA Boundaries...")
boundaries = gpd.read_file(f'{PATH}/raw/Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4_6453788336260919790.gpkg', use_arrow=True)
print(f"Found {boundaries.shape[0]} Rows.\n")


#--------Import LSOA Classifications--------#


print("Importing LSOA Classes...")
classes = pd.read_csv(f'{PATH}/raw/Rural_Urban_Classification_(2021)_of_LSOAs_in_EW.csv')
print(f"Found {classes.shape[0]} Rows.\n")


#--------Import ODS document---------#


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
lsoas.drop(["LSOA21NMW_x", "BNG_E", "BNG_N", "GlobalID", "LSOA21NM_y", "LSOA21NMW_y", "RUC21NM", "Urban_rural_flag", "ObjectId"], axis=1, inplace=True)
lsoas.rename({"LSOA21CD": "LSOACode", "LSOA21NM_x": "LSOAName", "LAT": "Latitude", "LONG": "Longitude", "RUC21CD": "RUCCode"}, axis=1, inplace=True)

# Save as a CSV
lsoas.to_file(f'{PATH}/processed/LSOA_Boundaries.gpkg', driver="GPKG", use_arrow=True)
print("Updated LSOA Dataset with RUC classifcations at 'processed/LSOA_Boundaries.gpkg'")

# Create a new GeoDataframe containing only point geometries at the centre of each LSOA
centre_df = lsoas.drop(["RUCCode", "geometry"], axis=1)
centre_gdf = gpd.GeoDataFrame(centre_df, geometry=gpd.points_from_xy(centre_df['Longitude'], centre_df['Latitude']), crs="EPSG:4326")
centre_gdf.to_file(f'{PATH}/processed/LSOA_Centres.gpkg', driver="GPKG", use_arrow=True)
print("Created LSOA Centres Dataset at 'processed/LSOA_Centres.gpkg'")


#--------Process employment centres-----------#


# Annonate each sheet with size of employment centre
sheets[1].insert(4, "Size", "Small")
sheets[2].insert(4, "Size", "Medium")
sheets[3].insert(4, "Size", "Large")

# Join sheets and sort by LSOA Code
employment_df = pd.concat([sheets[1], sheets[2], sheets[3]])
employment_df.sort_values("LSOACode", inplace=True)

# Save as a CSV
employment_df.to_csv(f'{PATH}/processed/employment_centres.csv', index=False)
print("Created Employment Centres Dataset at 'processed/employment_centres.csv'")


#--------Process other destinations-----------#


# Remame fields in GP and Hospitals to match schools
sheets[7].rename({"GP_Code": "URN", "Postcode": "EstablishmentName"}, axis=1, inplace=True)
sheets[8].rename({"SiteCode": "URN", "SiteName": "EstablishmentName"}, axis=1, inplace=True)

# Annonate each dataframe with type of destination
sheets[4].insert(4, "Type", "Primary School")
sheets[5].insert(4, "Type", "Secondary School")
sheets[6].insert(4, "Type", "Further Education")
sheets[7].insert(4, "Type", "GP")
sheets[8].insert(4, "Type", "Hospital")

# Join sheets and sort by LSOA Code
dest_df = pd.concat([sheets[4], sheets[5], sheets[6], sheets[7], sheets[8]])

# Save as a CSV
dest_df.to_csv(f'{PATH}/processed/destinations.csv', index=False)
print("Created Destinations Dataset at 'processed/destinations.csv'")
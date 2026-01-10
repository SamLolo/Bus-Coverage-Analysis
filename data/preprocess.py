import os 
import pandas as pd

PATH = os.path.dirname(os.path.realpath(__file__))


#--------Import LSOA Boundaries--------#


print("Importing LSOA Boundaries...")
boundaries = pd.read_csv(f'{PATH}/raw/Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4_3901388190129020682.csv')
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
lsoas = pd.merge(boundaries, classes, on='LSOA21CD', how="outer")

# Save RUC classification meanings seperately
ruc_def = pd.Series(classes['RUC21NM'].values, index = classes['RUC21CD'])
ruc_def.drop_duplicates(inplace=True)
ruc_def.to_json(f'{PATH}/processed/RUC_definitions.json', orient='index', indent=1)
print("Created RUC Definitions Dataset at 'processed/RUC_definitions.json'")

# Drop unwanted columns
lsoas.drop(["FID", "LSOA21NMW_x", "BNG_E", "BNG_N", "Shape__Area", "Shape__Length", "GlobalID", "LSOA21NM_y", "LSOA21NMW_y", "RUC21NM", "Urban_rural_flag", "ObjectId"], axis=1, inplace=True)
lsoas.rename({"LSOA21CD": "LSOACode", "LSOA21NM_x": "LSOAName", "LAT": "Latitude", "LONG": "Longitude", "RUC21CD": "RUCCode"}, axis=1, inplace=True)

# Save as a CSV
lsoas.to_csv(f'{PATH}/processed/LSOA_centres.csv', index=False)
print("Created LSOA Centre Point Dataset at 'processed/LSOA_centres.csv'")


#--------Process employment centres-----------#


# Annonate each sheet with size of employment centre
sheets[1].insert(4, "Size", "Small")
sheets[2].insert(4, "Size", "Medium")
sheets[3].insert(4, "Size", "Large")

# Join sheets and sort by LSOA Code
employment_df = pd.concat([sheets[1], sheets[2], sheets[3]])
employment_df.sort_values("LSOACode", inplace=True)

# Save as a CSV
employment_df.to_csv('data/processed/employment_centres.csv', index=False)
print("Created Employment Centres Dataset at 'processed/employment_centres.csv'")
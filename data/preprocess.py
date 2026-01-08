import pandas as pd

#--------Import ODS document---------#

print("Importing Destination Dataset...")
sheets = pd.read_excel('data/raw/journey-time-statistics-2019-destination-datasets.ods', sheet_name=[1, 2, 3, 4, 5, 6, 7, 8], header=2)
print(f"Found {len(sheets.keys())} Sheets!")

#--------Process employment centres-----------#

sheets[1].insert(4, "Size", "Small")
sheets[2].insert(4, "Size", "Medium")
sheets[3].insert(4, "Size", "Large")

employment_df = pd.concat([sheets[1], sheets[2], sheets[3]])
employment_df.sort_values("LSOACode", inplace=True)
employment_df.to_csv('data/processed/employment_centres.csv', index=False)
print("Created Employment Centres Dataset at 'processed/employment_centres.csv'.")
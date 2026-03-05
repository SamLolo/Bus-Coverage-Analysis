import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR, load_dataset, Datasets

# Load completed isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg", use_arrow=True)
car = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg", use_arrow=True)
print("Loaded isochrones")

# Load destinations
destinations = load_dataset(Datasets.DESTINATIONS)
print("Loaded destinations")

# Complete spatial join on all polygons and destinations
bus_intersects = destinations.sjoin(bus, how="inner", predicate="intersects")
print("Completed spatial-join with bus isochrones")
car_intersects = destinations.sjoin(car, how="inner", predicate="intersects")
print("Completed spatial-join with car isochrones")
    
# Count groups per id
bus_results = bus_intersects.groupby(['id', 'type'], sort=True).size().unstack().reset_index()
car_results = car_intersects.groupby(['id', 'type'], sort=True).size().unstack().reset_index()
print("Counted results")

# Merge with isochrone df to keep all lsoa ids and names
bus_results = pd.merge(bus, bus_results, on='id', how='left').fillna(0)
car_results = pd.merge(car, car_results, on='id', how='left').fillna(0)
print("Filled blank results")

# Drop gometry column from both dfs
bus_results.drop("geometry", axis=1, inplace=True)
car_results.drop("geometry", axis=1, inplace=True)

# Save individual calculations to csv
bus_results.to_csv(OUT_DIR / f"bus_destinations.csv")
car_results.to_csv(OUT_DIR / f"car_destinations.csv")
print("Saved to individual files")

# Sum totals for each category
totals = {
    "id": bus_results['id'],
    "name": bus_results['name']
}
totals['employment_bus'] = bus_results[['small_employment', 'medium_employment', 'large_employment']].sum(axis=1)
totals['employment_car'] = car_results[['small_employment', 'medium_employment', 'large_employment']].sum(axis=1)
totals['education_bus'] = bus_results[['primary_school', 'secondary_school', 'further_education']].sum(axis=1)
totals['education_car'] = car_results[['primary_school', 'secondary_school', 'further_education']].sum(axis=1)
totals['healthcare_bus'] = bus_results[['gp', 'hospital']].sum(axis=1)
totals['healthcare_car'] = car_results[['gp', 'hospital']].sum(axis=1)

# Create dataframe
totals_df = pd.DataFrame(totals)

# Calculate overall totals
totals_df['total_bus'] = totals_df[['employment_bus', 'education_bus', 'healthcare_bus']].sum(axis=1)
totals_df['total_car'] = totals_df[['employment_car', 'education_car', 'healthcare_car']].sum(axis=1)
print("Calculated category totals")

# Calculate ratios for each category
totals_df['employment_ratio'] = totals_df['employment_bus'] / totals_df['employment_car']
totals_df['education_ratio'] = totals_df['education_bus'] / totals_df['education_car']
totals_df['healthcare_ratio'] = totals_df['healthcare_bus'] / totals_df['healthcare_car']
totals_df['ratio'] = totals_df['total_bus'] / totals_df['total_car']
print("Calculated category ratios")

# Fill any ratios using 0 for those that returned None due to 0/0 error
totals_df = totals_df.fillna(0.0)

# Save to csv file
totals_df.to_csv(OUT_DIR / f"destination_totals.csv")
print("Saved to file")

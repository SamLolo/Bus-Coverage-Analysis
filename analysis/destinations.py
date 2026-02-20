import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR, load_dataset, Datasets

# Load completed isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg", use_arrow=True)
car = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg", use_arrow=True)

# Load destinations
destinations = load_dataset(Datasets.DESTINATIONS)

bus_intersects = destinations.sjoin(bus, how="inner", predicate="intersects")
car_intersects = destinations.sjoin(car, how="inner", predicate="intersects")
    
# Count groups per id
bus_results = bus_intersects.groupby(['id', 'type'], sort=True).size().unstack().reset_index()
car_results = car_intersects.groupby(['id', 'type'], sort=True).size().unstack().reset_index()

# Merge with isochrone df to keep all lsoa ids and names
bus_results = pd.merge(bus, bus_results, on='id', how='left').fillna(0)
car_results = pd.merge(car, car_results, on='id', how='left').fillna(0)

# Drop gometry column from both dfs
bus_results.drop("geometry", axis=1, inplace=True)
car_results.drop("geometry", axis=1, inplace=True)

# Save individual calculations to csv
bus_results.to_csv(OUT_DIR / f"bus_destinations.csv")
car_results.to_csv(OUT_DIR / f"car_destinations.csv")

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

# Calculate ratios for each category
totals_df['employment_ratio'] = totals_df['employment_bus'] / totals_df['employment_car']
totals_df['education_ratio'] = totals_df['education_bus'] / totals_df['education_car']
totals_df['healthcare_ratio'] = totals_df['healthcare_bus'] / totals_df['healthcare_car']

# Calculate overall totals and ratios
totals_df['total_bus'] = totals_df[['employment_bus', 'education_bus', 'healthcare_bus']].sum(axis=1)
totals_df['total_car'] = totals_df[['employment_car', 'education_car', 'healthcare_car']].sum(axis=1)
totals_df['ratio'] = totals_df['total_bus'] / totals_df['total_car']

# Save to csv file
totals_df.to_csv(OUT_DIR / f"destination_totals.csv")

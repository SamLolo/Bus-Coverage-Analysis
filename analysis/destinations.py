import pandas as pd
import geopandas as gpd
from common.data import OUT_DIR, load_dataset, Datasets

# Load completed isochrones
bus = gpd.read_file(OUT_DIR / "bus_isochrones_combined.gpkg", use_arrow=True)
car = gpd.read_file(OUT_DIR / "car_isochrones_combined.gpkg", use_arrow=True)

# Load destinations
destinations = load_dataset(Datasets.DESTINATIONS)

# Treat each isochrones file seperately
for df_name, isochrone_df in [("bus", bus), ("car", car)]:
    
    # Complete spatial join
    intersects = destinations.sjoin(isochrone_df, how="inner", predicate="intersects")
    
    # Count groups per id
    count = intersects.groupby(['id', 'type']).size()
    results = count.unstack().reset_index()
    
    # Merge with isochrone df to keep all lsoa ids and names
    results = pd.merge(isochrone_df, results, on='id', how='left').fillna(0)
    results.drop("geometry", axis=1, inplace=True)
    
    # Sum totals for each category
    results['employment_total'] = results[['small_employment', 'medium_employment', 'large_employment']].sum(axis=1)
    results['education_total'] = results[['primary_school', 'secondary_school', 'further_education']].sum(axis=1)
    results['healthcare_total'] = results[['gp', 'hospital']].sum(axis=1)
    results['total_all'] = results[['employment_total', 'education_total', 'healthcare_total']].sum(axis=1)
    
    # Save to csv file
    results.to_csv(OUT_DIR / f"{df_name}_destinations.csv")
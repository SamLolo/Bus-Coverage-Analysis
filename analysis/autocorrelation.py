import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)
removed = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg", use_arrow=True)
lsoas = lsoas[~lsoas['id'].isin(removed['id'])]

#print(lsoas.iloc[18090])
#print(lsoas.iloc[27353])

# Load other spatial indicators
areas = pd.read_csv(OUT_DIR / "areas.csv")
destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")

y = destinations['education_ratio']
print(destinations[y.isna()])
print(destinations[np.isinf(y.values)])
print(y.values.var())

# Create spatial weights matrix
weights = Queen.from_dataframe(lsoas)
weights.set_transform("R")

# Which indicators to use for calculations
indicators = {
    "areas": areas['ratio'],
    "employment": destinations['employment_ratio'],
    "education": destinations['education_ratio'],
    "healthcare": destinations['healthcare_ratio'],
    "destinations": destinations['ratio']
}

# Calculate global Moran's I
global_results = pd.DataFrame(columns=["indicator", "morans_i", "p-test"])
for i, key in enumerate(indicators.keys()):
    morans = Moran(indicators[key], weights)
    global_results.loc[i] = [key, morans.I, morans.p_sim]
    
# Save global results to file
global_results.to_csv(OUT_DIR / "global_morans_i.csv")

def calculate_correlation(values: pd.Series) -> pd.DataFrame:
    # Create dataframe
    results = lsoas[["id", "name"]].copy()

    # Calculate local Moran's I
    lisa = Moran_Local(values, weights)
    results["morans_i"] = lisa.Is
    results["p-value"] = lisa.p_sim
    results["type"] = lisa.q
    return results

# Accessibility Indicator 1
area_correlation = calculate_correlation(areas['ratio'])
area_correlation.to_csv(OUT_DIR / "area_correlations.csv")
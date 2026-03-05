import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)
removed = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg", use_arrow=True)
lsoas = lsoas[~lsoas['id'].isin(removed['id'])]
print("Loaded LSOA boundaries")

# Load other spatial indicators
areas = pd.read_csv(OUT_DIR / "areas.csv")
destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")
print("Loaded accessibility indicator calculations")

# Merge areas to create single dataframe
lsoas = pd.merge(lsoas, areas, how="left", on="id")
lsoas.drop(["Unnamed: 0", "name_y"], axis=1, inplace=True)
lsoas.rename({"name_x": "name", "ratio": "areas_ratio"}, axis=1, inplace=True)

# Merge destinations to create single dataframe
lsoas = pd.merge(lsoas, destinations, how="left", on="id")
lsoas.drop(["Unnamed: 0", "name_y"], axis=1, inplace=True)
lsoas.rename({"name_x": "name", "ratio": "destinations_ratio"}, axis=1, inplace=True)
print("Created single master dataframe")

# Remove Isles of Scilly as it's spatially seperate
lsoas = lsoas[lsoas['id'] != "E01019077"]
print("Removed 'E01019077: ISLES OF SCILLY' as it's spatially seperate")

# Create spatial weights matrix
weights = Queen.from_dataframe(lsoas, ids="id")
weights.set_transform("R")
print("Created weights matrix")

# Which indicators to use for calculations
indicators = {
    "bus_area": lsoas['bus_area'].values,
    "car_area": lsoas['car_area'].values,
    "areas_ratio": lsoas['areas_ratio'].values,
    "employment": lsoas['employment_ratio'].values,
    "education": lsoas['education_ratio'].values,
    "healthcare": lsoas['healthcare_ratio'].values,
    "bus_destinations": lsoas['total_bus'].values,
    "car_destinations": lsoas['total_car'].values,
    "destinations_ratio": lsoas['destinations_ratio'].values
}

# Calculate global Moran's I
global_results = pd.DataFrame(columns=["indicator", "morans_i", "p-test"])
for i, key in enumerate(indicators.keys()):
    morans = Moran(indicators[key], weights)
    global_results.loc[i] = [key, morans.I, morans.p_sim]
    
# Save global results to file
global_results.to_csv(OUT_DIR / "correlations" / "global_correlations.csv")
print("Calculated global Moran's I")

# Calculaye LISA correlation for each indicator
for name, values in indicators.items():
    results = lsoas[["id", "name"]].copy()

    # Calculate local Moran's I
    lisa = Moran_Local(values, weights)
    results["morans_i"] = lisa.Is
    results["p-value"] = lisa.p_sim
    
    # Determine clustering by looking at permuation test
    clustering = []
    for i in range(len(lisa.q)):
        if lisa.p_sim[i] >= 0.05:
            clustering.append("not significant")
        else:
            match lisa.q[i]:
                case 1:
                    clustering.append("high-high")
                case 2:
                    clustering.append("low-high")
                case 3:
                    clustering.append("low-low")
                case 4:
                    clustering.append("high-low")
    results["quadrant"] = lisa.q
    results["clustering"] = clustering
    
    # Save results dataframe to csv file
    results.to_csv(OUT_DIR / "correlations" / f"{name}_correlations.csv")
    print("Calculated LISA values for indicator:", name)
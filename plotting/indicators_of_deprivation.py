import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from common.data import OUT_DIR, Datasets, get_filepath, load_dataset

# Read indicies of multiple deprivation for 2025
sheet = pd.read_excel(get_filepath(Datasets.IMD), sheet_name=[1], index_col=0, engine='calamine')
imd = sheet[1]['Index of Multiple Deprivation (IMD) Score']

# Load area and destination ratio results
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv")

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Align results into a single dataframe
results = lsoas.merge(areas, on="id")
results = results.merge(destinations, on="id")
results = results.merge(imd, left_on="id", right_index=True)

# Drop extra columns and rename to make columns more friendly
results = results[["id", "name_x", "ruc", "ratio_x", "ratio_y", "Index of Multiple Deprivation (IMD) Score"]]
results.rename({"name_x": "name", "ratio_x": "area_ratio", "ratio_y": "destinations_ratio", "Index of Multiple Deprivation (IMD) Score": "imd_score"}, axis=1, inplace=True)

# Seperate urban and rural results
urban = results[results['ruc'].isin(["UN1", "UF1"])]
rural = results[results['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]

# Calculate pearson correlation for area and destinations
for key, df in {"Overall": results, "Urban": urban, "Rural": rural}.items():
    print(f"{key} Results:")
    area_corr = pearsonr(df['area_ratio'], df['imd_score'])
    print(f"   Area Correlation: {area_corr[0]:.3f} (p {'< 0.001' if area_corr[1] < 0.001 else f'= {area_corr[1]:.2f}'})")
    dest_corr = pearsonr(df['destinations_ratio'], df['imd_score'])
    print(f"   Destination Correlation: {dest_corr[0]:.3f} (p {'< 0.001' if dest_corr[1] < 0.001 else f'= {dest_corr[1]:.2f}'})")
    
# Plot each onto a scattergraph with different colours
plt.scatter(urban['destinations_ratio'], urban['imd_score'], color="blue", alpha=0.5, s=10, label="Urban LSOAs")
plt.scatter(rural['destinations_ratio'], rural['imd_score'], color="orange", alpha=0.5, s=10, label="Rural LSOAs")

# Convert to log scale
plt.xscale("log")
#plt.yscale("log")

# Add title and labels
plt.title('Alignment with 2025 Indicators of Deprivation')
plt.xlabel('Destinations Ratio')
plt.ylabel('IMD Score')

# Add legend
plt.legend(loc="upper left")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "imd_destinations_scatterplot.png", dpi=600)
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load isochrone area values
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")
areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

# Create single dataframe with destination results
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv")
results = pd.merge(areas, destinations, on="id")

# Create seperate dataframes for rural and urban LSOAs
urban = results[results['ruc'].isin(["UN1", "UF1"])]
print(f"Percentage Urban: {(urban.shape[0] / results.shape[0]) * 100:.1f}%")
rural = results[results['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]
print(f"Percentage Rural: {(rural.shape[0] / results.shape[0]) * 100:.1f}%")

# Calculate correlation coefficients
car_coef = pearsonr(results['car_area'], results['total_car'])
print(f"Car-Destinations Correlation Coefficient: {car_coef.statistic:.2f} ({car_coef.pvalue})")
bus_coef = pearsonr(results['bus_area'], results['total_bus'])
print(f"Bus-Destinations Correlation Coefficient: {bus_coef.statistic:.2f} ({bus_coef.pvalue})")

# Plot each onto a scattergraph with different colours
plt.scatter(results['car_area'], results['total_car'], color="blue", alpha=0.5, s=10, label="Driving")
plt.scatter(results['bus_area'], results['total_bus'], color="red", alpha=0.5, s=10, label="Bus + Walking")

# Add title and labels
plt.title('How Isochrone Size Affects Destinations')
plt.xlabel('Size of Isochrone (km²)')
plt.ylabel('Number of Destinations')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Add legend
plt.legend(loc="upper left", fontsize=9, markerscale=2)

# Save to png
plt.savefig(OUT_DIR / "plots" / "size_destinations_scatterplot.png", dpi=600)
plt.close()


# ---------------------------------
#
#        RATIOS COMPARISON
#
# ---------------------------------

# Calculate correlation coefficients
urban_coef = pearsonr(urban['ratio_x'], urban['ratio_y'])
print(f"[URBAN] Area-Destinations Correlation Coefficient: {urban_coef.statistic:.2f} ({urban_coef.pvalue})")
rural_coef = pearsonr(rural['ratio_x'], rural['ratio_y'])
print(f"[RURAL] Area-Destinations Correlation Coefficient: {rural_coef.statistic:.2f} ({rural_coef.pvalue})")

# Filter out outliers
urban = urban[(urban['ratio_x'] < 0.3) & (urban['ratio_y'] < 1)]
rural = rural[(rural['ratio_x'] < 0.3) & (rural['ratio_y'] < 1)]

# Plot area to destinations as scatterplot with different colours for urban-rural
plt.scatter(urban['ratio_x'], urban['ratio_y'], color="#1a80bb", alpha=0.75, s=0.5, label="Urban LSOAs")
plt.scatter(rural['ratio_x'], rural['ratio_y'], color="#ea801c", alpha=0.75, s=0.5, label="Rural LSOAs")

# Add title and labels
plt.title('Comparison of Indicator Values by Settlement Type')
plt.xlabel('Area Ratio')
plt.ylabel('Destinations Ratio')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Save to png
plt.legend(loc="upper right", markerscale=8)
plt.tight_layout()
plt.savefig(OUT_DIR / "plots" / "area_destinations_scatterplot.png", dpi=600)
plt.close()


# ---------------------------------
#
#           BUS ONLY
#
# ---------------------------------

# Plot area to destinations as scatterplot by ruc classification
plt.scatter(urban['bus_area'], urban['total_bus'], color="#1a80bb", alpha=0.75, s=0.5, label="Urban LSOAs")
plt.scatter(rural['bus_area'], rural['total_bus'], color="#ea801c", alpha=0.75, s=0.5, label="Rural LSOAs")

# Add line of best fit
slope, intercept = np.polyfit(results['bus_area'], results['total_bus'], 1)
plt.plot(results['bus_area'], slope*results['bus_area'] + intercept, color='dimgrey', linestyle='solid', linewidth=1.5, label='Best Fit Line')
plt.legend(loc="upper left", fontsize=10, markerscale=8)

# Add title and labels
plt.title('How Bus Coverage Affects Destinations')
plt.xlabel('Size of Isochrone (km²)')
plt.ylabel('Number of Destinations')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Save to png
plt.savefig(OUT_DIR / "plots" / "bus_size_destinations_scatterplot.png", dpi=600)
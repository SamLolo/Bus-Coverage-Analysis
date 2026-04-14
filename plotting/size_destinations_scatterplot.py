import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from common.data import OUT_DIR

# Load areas and destination results
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv")

# Create single dataframe
results = pd.merge(areas, destinations, on="id")

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
#           BUS ONLY
#
# ---------------------------------

# Plot area to destinations as scatterplot
plt.scatter(results['bus_area'], results['total_bus'], color="blue", alpha=0.5, s=10, label="LSOAs")

# Add line of best fit
slope, intercept = np.polyfit(results['bus_area'], results['total_bus'], 1)
plt.plot(results['bus_area'], slope*results['bus_area'] + intercept, color='dimgrey', linestyle='solid', linewidth=1.5, label='Best Fit Line')
plt.legend(loc="upper left", fontsize=10, markerscale=2.5)

# Add title and labels
plt.title('How Bus Coverage Affects Destinations')
plt.xlabel('Size of Isochrone (km²)')
plt.ylabel('Number of Destinations')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Save to png
plt.savefig(OUT_DIR / "plots" / "bus_size_destinations_scatterplot.png", dpi=600)
plt.close()

# ---------------------------------
#
#        RATIOS COMPARISON
#
# ---------------------------------

# Plot area to destinations as scatterplot
plt.scatter(results['ratio_x'], results['ratio_y'], color="blue", alpha=0.5, s=10)

# Add title and labels
plt.title('Comparison of Indicator Values')
plt.xlabel('Area Ratio')
plt.ylabel('Destinations Ratio')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Save to png
plt.savefig(OUT_DIR / "plots" / "area_destinations_scatterplot.png", dpi=600)
import pandas as pd
import matplotlib.pyplot as plt
from common.data import OUT_DIR

# Load areas and destination results
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv")

# Create single dataframe
results = pd.merge(areas, destinations, on="id")

# Plot each onto a scattergraph with different colours
plt.scatter(results['car_area'], results['total_car'], color="blue", alpha=0.5, s=10, label="Driving")
plt.scatter(results['bus_area'], results['total_bus'], color="red", alpha=0.5, s=10, label="Bus + Walking")

# Add title and labels
plt.title('How Isochrone Size Affects Destinations')
plt.xlabel('Size of Isochrone (km²)')
plt.ylabel('Number of Destinations')

# Add legend
plt.legend(loc="upper left")

# Save to png
plt.savefig(OUT_DIR / "plots" / "size_destinations_scatterplot.png", dpi=600)
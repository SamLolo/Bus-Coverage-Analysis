import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load isochrone destination totals
destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")
destinations: gpd.GeoDataFrame = lsoas.merge(destinations, on="id")

# Create seperate dataframes for rural and urban LSOAs
urban = destinations[destinations['ruc'].isin(["UN1", "UF1"])]
rural = destinations[destinations['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]

# Plot each onto a scattergraph with different colours
plt.scatter(urban['total_car'], urban['total_bus'], color="blue", alpha=0.5, s=10, label="Urban LSOAs")
plt.scatter(rural['total_car'], rural['total_bus'], color="orange", alpha=0.5, s=10, label="Rural LSOAs")

# Convert to log scale
plt.xscale("log")
plt.yscale("log")

# Add title and labels
plt.title('Accessibility gap in opportunities between transport modes')
plt.xlabel('Destinations by Car')
plt.ylabel('Destinations by Bus')

# Set axis limits to data
x_lim = plt.xlim()
y_lim = plt.ylim()
limits = [max(x_lim[0], y_lim[0]), max(x_lim[1], y_lim[1])]
plt.xlim(limits)
plt.ylim(limits)

# Add line of equality
plt.plot(limits, limits, color='black', linewidth=1.5, label="Equal Opportunity")

# Add legend
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25), ncol=3)
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "destinations_scatterplot.png", dpi=300)
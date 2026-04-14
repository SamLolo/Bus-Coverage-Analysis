import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load destinations and merge with LSOA boundaries
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv")
destinations: gpd.GeoDataFrame = lsoas.merge(destinations, on="id")

# Print out some statistics
print("\nRATIO:")
print(f"Mean: {destinations['ratio'].mean():.4f}")
print(f"Median: {destinations['ratio'].median():.4f}")
print(f"Range: {(destinations['ratio'].max() - destinations['ratio'].min()):.4f}")
print(f"Std: {destinations['ratio'].std():.4f}")
print(f"Above 0.05: {(destinations['ratio'] >= 0.05).mean() * 100:.1f}%")
print(f"Above 0.10: {(destinations['ratio'] >= 0.1).mean() * 100:.1f}%")
print(f"Above 0.50: {(destinations['ratio'] >= 0.5).mean() * 100:.1f}%")

# Create ticks
ticks = [round(n, 3) for n in np.linspace(np.percentile(destinations['ratio'], 5), np.percentile(destinations['ratio'], 95), 4)]

# Create map plot between 5th and 95th percentiles
destinations.plot(column="ratio", 
                  cmap="plasma", 
                  vmin=np.percentile(destinations['ratio'], 5), 
                  vmax=np.percentile(destinations['ratio'], 95), 
                  legend=True,
                  legend_kwds={
                    "label": "Bus/Car Destination Ratio",
                    "ticks": ticks
                  })

# Turn axis off
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "destination_map.png", dpi=600)
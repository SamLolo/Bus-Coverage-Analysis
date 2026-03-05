import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load area indicator values
areas = pd.read_csv(OUT_DIR / "areas.csv")
areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

# Create logarithmic bin distribution
_, bins = np.histogram(areas['ratio'], bins=200)
log_bins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), 200)

# Plot ratio on a log scale
plt.hist(areas['ratio'], bins=log_bins)
plt.xscale('log')

# Add labels to graph
plt.xlabel('Bus / Car Area Ratio')
plt.ylabel('Number of LSOAs')
plt.title('Distribution of Access Areas')

# Save to png
plt.savefig(OUT_DIR / 'plots' / 'area_ratio_histogram.png', dpi=300)
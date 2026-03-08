import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from common.data import OUT_DIR

# Load area indicator values
areas = pd.read_csv(OUT_DIR / "areas.csv")

# ---------------------
#
#     NORMAL AXIS
#
# ---------------------

# Plot ratio on a normal scale
plt.hist(areas[areas['ratio'] < np.percentile(areas['ratio'], 99)]['ratio'], bins=100)

# Add labels to graph
plt.xlabel('Bus / Car Area Ratio')
plt.ylabel('Number of LSOAs')
plt.title('Distribution of Access Areas')

# Save to png
plt.savefig(OUT_DIR / 'plots' / 'area_ratio_histogram.png', dpi=600)
plt.close()

# ---------------------
#
#     LOG AXIS
#
# ---------------------

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
plt.savefig(OUT_DIR / 'plots' / 'area_ratio_histogram_log.png', dpi=600)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from common.data import OUT_DIR

# Load area indicator values
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")

# Plot ratio on a histogram
plt.hist(areas[areas['ratio'] < np.percentile(areas['ratio'], 99)]['ratio'], bins=100)

# Add labels to graph
plt.xlabel('Bus / Car Area Ratio')
plt.ylabel('Number of LSOAs')
plt.title('Distribution of Access Areas')

# Save to png
plt.savefig(OUT_DIR / 'plots' / 'area_ratio_histogram.png', dpi=600)
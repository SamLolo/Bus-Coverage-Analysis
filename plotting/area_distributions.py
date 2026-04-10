import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from common.data import OUT_DIR

# Load area indicator values
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")

# Print out some statistics
print("\nRATIO:")
print(f"Mean: {areas['ratio'].mean():.4f}")
print(f"Median: {areas['ratio'].median():.4f}")
print(f"Range: {(areas['ratio'].max() - areas['ratio'].min()):.4f}")
print(f"Std: {areas['ratio'].std():.4f}")
print(f"Below 0.01: {(areas['ratio'] < 0.01).mean() * 100:.1f}%")
print(f"Below 0.05: {(areas['ratio'] < 0.05).mean() * 100:.1f}%")

print("\nBUS ISOCHRONES:")
print(f"Mean: {areas['bus_area'].mean():.2f} km²")
print(f"Median: {areas['bus_area'].median():.2f} km²")
print(f"Range: {(areas['bus_area'].max() - areas['bus_area'].min()):.2f} km²")
print(f"Max: {areas['bus_area'].max():.2f} km²")
print(f"Std: {areas['bus_area'].std():.2f} km²")

print("\nCAR ISOCHRONES:")
print(f"Mean: {areas['car_area'].mean():.2f} km²")
print(f"Median: {areas['car_area'].median():.2f} km²")
print(f"Range: {(areas['car_area'].max() - areas['car_area'].min()):.2f} km²")
print(f"Max: {areas['car_area'].max():.2f} km²")
print(f"Std: {areas['car_area'].std():.2f} km²")

# Create plot with 2 axis side by side
_, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4), width_ratios=[4.75, 4.75, 5.5])

# -----------------------------
#
#       OVERALL RATIO
#
# -----------------------------s

# Plot ratio on a histogram
ax3.hist(areas[areas['ratio'] < np.percentile(areas['ratio'], 99)]['ratio'], bins=100, color="#b8b8b8")

# Add labels to graph
ax3.set_xlabel('Bus / Car Area Ratio')
ax3.set_ylabel(None)
ax3.set_title("Access Area Ratio")

# -----------------------------
#
#           BUS AREA
#
# -----------------------------

# Plot ratio on a histogram
ax1.hist(areas[areas['bus_area'] < np.percentile(areas['bus_area'], 99)]['bus_area'], bins=100, color="#a00000")
ax1.yaxis.set_major_locator(MaxNLocator(nbins=5))

# Add labels to graph
ax1.set_xlabel("Isochrone Size (km²)")
ax1.set_ylabel('Number of LSOAs')
ax1.set_title('Bus & Walking')

# -----------------------------
#
#           CAR AREA
#
# -----------------------------

# Plot ratio on a histogram
ax2.hist(areas[areas['car_area'] < np.percentile(areas['car_area'], 99)]['car_area'], bins=100, color="#1a80bb")
ax2.yaxis.set_major_locator(MaxNLocator(nbins=5))

# Add labels to graph
ax2.set_xlabel("Isochrone Size (km²)")
ax2.set_ylabel(None)
ax2.set_title('Driving')

# Save to png
plt.savefig(OUT_DIR / 'plots' / 'area_histograms.png', dpi=600, bbox_inches='tight', pad_inches=0.1)
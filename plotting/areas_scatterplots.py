import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load isochrone area values
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv")
areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

# Create seperate dataframes for rural and urban LSOAs
urban = areas[areas['ruc'].isin(["UN1", "UF1"])]
rural = areas[areas['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]

# Plot each onto a scattergraph with different colours
plt.scatter(urban['car_area'], urban['bus_area'], color="#1a80bb", alpha=0.75, s=0.5, label="Urban LSOAs")
plt.scatter(rural['car_area'], rural['bus_area'], color="#ea801c", alpha=0.75, s=0.5, label="Rural LSOAs")

# Add title and labels
plt.title('Isochrone Size By Rural-Urban Classification')
plt.xlabel('Size of Car Isochrone (km²)')
plt.ylabel('Size of Bus Isochrone (km²)')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Add legend
plt.legend(loc="upper right", fontsize=12, markerscale=8)
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "areas_scatterplot.png", dpi=600)
plt.close()

# ---------------------------------------------------
#
#              BUS TO RATIO SCATTERPLOT
#
# ---------------------------------------------------

# Plot bus to area ratio
coef = pearsonr(areas['ratio'], areas['bus_area'])
print(f"Bus-Ratio Correlation Coefficient: {coef.statistic:.2f} ({coef.pvalue})")
plt.scatter(areas['ratio'], areas['bus_area'], color="#1a80bb", alpha=0.75, s=1, label="LSOAs")

# Add line of best fit
subset = areas[areas['ratio'] < 0.3]
slope, intercept = np.polyfit(areas['ratio'], areas['bus_area'], 1)
plt.plot(subset['ratio'], slope*subset['ratio'] + intercept, color='dimgrey', linestyle='solid', linewidth=1.5, label='Best Fit Line')
plt.legend(loc="upper right", fontsize=12, markerscale=8)

# Add title and labels
plt.title('Relationship Between Bus Coverage and Ratio')
plt.xlabel('Bus/Car Area Ratio')
plt.ylabel('Size of Isochrone (km²)')
plt.xlim(left=0)
plt.ylim(bottom=0)

# Save to png
plt.tight_layout()
plt.savefig(OUT_DIR / "plots" / "bus_area_to_ratio_scatterplot.png", dpi=600)
plt.close()
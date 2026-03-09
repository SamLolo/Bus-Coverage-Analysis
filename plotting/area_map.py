import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load areas and merge with LSOA boundaries
areas = pd.read_csv(OUT_DIR / "areas.csv")
areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

# Create ticks
ticks = [round(n, 3) for n in np.linspace(np.percentile(areas['ratio'], 10), np.percentile(areas['ratio'], 90), 4)]

# Create map plot between 10th and 90th percentiles
areas.plot(column="ratio", 
           cmap="viridis", 
           vmin=np.percentile(areas['ratio'], 10), 
           vmax=np.percentile(areas['ratio'], 90), 
           legend=True,
           legend_kwds={
               "label": "Bus/Car Area Ratio",
               "ticks": ticks
            })

# Turn axis off
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "area_map.png", dpi=600)
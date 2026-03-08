import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load destinations and merge with LSOA boundaries
destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")
destinations: gpd.GeoDataFrame = lsoas.merge(destinations, on="id")

# Create map plot between 5th and 95th percentiles
destinations.plot(column="ratio", 
                  cmap="plasma", 
                  vmin=np.percentile(destinations['ratio'], 5), 
                  vmax=np.percentile(destinations['ratio'], 95), 
                  legend=True,
                  legend_kwds={"label": "Bus/Car Destination Ratio"})

# Turn axis off
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "destination_map.png", dpi=600)
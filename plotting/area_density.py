import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load isochrone area values
areas = pd.read_csv(OUT_DIR / "areas.csv")
areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

# Create seperate dataframes for rural and urban LSOAs
urban = areas[areas['ruc'].isin(["UN1", "UF1"])]
rural = areas[areas['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]

# Create plot with 2 axis side by side
_, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Plot left density plot (bus)
urban['bus_area'].plot.kde(ax=ax1, color="red")
rural['bus_area'].plot.kde(ax=ax1, color="blue")

# Plot right density plot (car)
urban['car_area'].plot.kde(ax=ax2, color="red")
rural['car_area'].plot.kde(ax=ax2, color="blue")

# Add axis labels
ax1.set_xlabel("Isochrone Size (km²)")
ax2.set_xlabel("Isochrone Size (km²)")

# Add titles
ax1.set_title("Bus Isochrones")
ax2.set_title("Car Isochrones")

# Save to png
plt.tight_layout()
plt.savefig(OUT_DIR / "plots" / "area_density.png", dpi=600)
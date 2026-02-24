import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

areas = pd.read_csv(OUT_DIR / "areas.csv")

areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

print(areas['ratio'].min(), areas['ratio'].max())
print(np.percentile(areas['ratio'], [1, 5, 10, 50, 90, 95, 99]))

areas.plot(column="ratio", cmap="viridis", vmin=np.percentile(areas['ratio'], 10), vmax=np.percentile(areas['ratio'], 90))
plt.show()
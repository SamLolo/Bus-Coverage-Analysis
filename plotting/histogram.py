import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

areas = pd.read_csv(OUT_DIR / "areas.csv")
areas: gpd.GeoDataFrame = lsoas.merge(areas, on="id")

areas = areas[areas['ratio'] < np.percentile(areas['ratio'], 99)]

plt.hist(areas['ratio'], bins=100)
plt.xlabel('Bus / Car Area Ratio')
plt.ylabel('Number of LSOAs')
plt.title('Distribution of Access Areas')
plt.show()
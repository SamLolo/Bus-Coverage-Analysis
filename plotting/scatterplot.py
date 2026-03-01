import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")
destinations: gpd.GeoDataFrame = lsoas.merge(destinations, on="id")

urban = destinations[destinations['ruc'].isin(["UN1", "UF1"])]
rural = destinations[destinations['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]

plt.title('Accessibility gap in opportunities between transport modes')

plt.scatter(urban['total_car'], urban['total_bus'], color="blue", alpha=0.3, s=10)
plt.scatter(rural['total_car'], rural['total_bus'], color="orange", alpha=0.3, s=10)

plt.xlabel('Destinations by Car')
plt.ylabel('Destinations by Bus')

x_lim = plt.xlim()
y_lim = plt.ylim()

limits = [max(x_lim[0], y_lim[0]), max(x_lim[1], y_lim[1])]
plt.xlim(limits)
plt.ylim(limits)

plt.plot(limits, limits, color='black', linewidth=2)
plt.text(6500, 6800, "Equal opportunity", rotation=36)

plt.show()
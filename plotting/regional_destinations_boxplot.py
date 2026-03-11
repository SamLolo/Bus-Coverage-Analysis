import pandas as pd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.CENTRIODS)
regions = load_dataset(Datasets.REGIONS)

# Load isochrone destination totals
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv")
destinations = lsoas.merge(destinations, on="id")

# Group lsoas by region
overlay = regions.sjoin(destinations, predicate="contains")
groups = overlay.groupby(["id_left", "name_left"])

# Create a stacked vertical plot of each type of ratio
plt.boxplot([group["ratio"] for _, group in groups],
             orientation="horizontal",
             showfliers=False,
             tick_labels=[name for (_, name), _ in groups])

# Add title
plt.title("Accessibility Distribution by Region")
plt.xlabel("Bus/Car Destination Ratio")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "regions_destinations_boxplot.png", dpi=600)
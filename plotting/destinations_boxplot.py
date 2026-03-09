import pandas as pd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

# Load isochrone destination totals
destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")
destinations = lsoas.merge(destinations, on="id")

# Create seperate dataframes for rural and urban LSOAs
urban = destinations[destinations['ruc'].isin(["UN1", "UF1"])]
rural = destinations[destinations['ruc'].isin(["RSN1", "RLN1", "RLF1", "RSF1"])]

# Create a stacked vertical plot of each type of ratio
plt.boxplot([rural['education_ratio'], urban['education_ratio'], rural['healthcare_ratio'], urban['healthcare_ratio'], 
             rural['employment_ratio'], urban['employment_ratio'], rural['ratio'], urban['ratio']],
             orientation="horizontal",
             showfliers=False,
             tick_labels=["Education (Rural)", "Education (Urban)", "Healthcare (Rural)", "Healthcare (Urban)", 
                          "Employment (Rural)", "Employment (Urban)", "Overall (Rural)", "Overall (Urban)"])

# Add title
plt.title("Accessibility Distribution by Destination Type")
plt.xlabel("Bus/Car Destination Ratio")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "destinations_boxplot.png", dpi=600)
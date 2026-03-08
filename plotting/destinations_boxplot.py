import pandas as pd
import matplotlib.pyplot as plt
from common.data import OUT_DIR

# Load destinations and merge with LSOA boundaries
destinations = pd.read_csv(OUT_DIR / "destination_totals.csv")

# Create a stacked vertical plot of each type of ratio
plt.boxplot([destinations['education_ratio'], destinations['healthcare_ratio'], destinations['employment_ratio'], destinations['ratio']],
            orientation="horizontal",
            showfliers=False,
            tick_labels=["Education", "Healthcare", "Employment", "Overall"])

# Add title
plt.title("Accessibility Distribution by Destination Type")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "destinations_boxplot.png", dpi=600)
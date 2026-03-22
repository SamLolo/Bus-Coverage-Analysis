import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from common.data import OUT_DIR, load_dataset, Datasets

# Load and re-categorise destinations
destinations = load_dataset(Datasets.DESTINATIONS)
destinations['type'] = destinations['type'].replace({
    "small_employment": "Employment",
    "medium_employment": "Employment",
    "large_employment": "Employment",
    "primary_school": "Education",
    "secondary_school": "Education",
    "further_education": "Education",
    "gp": "Healthcare",
    "hospital": "Healthcare"
})

# Plot the county boundaries
regions = load_dataset(Datasets.COUNTIES)
ax = regions.boundary.plot(
    color="black",
    linewidth=0.2
)

# Create colourmap
colours = {
    "Employment": "#003a76",
    "Education": "#4ecb8d",
    "Healthcare": "#ff73b6"
}
cmap = ListedColormap([colours[name] for name in destinations['type'].unique()])

# Plot the destinations
destinations.plot(
    column="type",
    cmap=cmap,
    ax=ax,
    markersize=0.2,
    alpha=0.5,
    legend=True
)

# Turn axis off
plt.axis("off")
plt.tight_layout()

# Save to png
plt.savefig(OUT_DIR / "plots" / "destination_density.png", dpi=600)
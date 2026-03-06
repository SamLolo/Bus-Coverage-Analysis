import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from common.data import OUT_DIR, load_dataset, Datasets

# Load LSOA boundaries
lsoas = load_dataset(Datasets.LSOA_BOUNDARIES)

"""
Wrapper function for creating a cloropleth map of local clustering in the UK using LISA values
defined within a CSV file.

Args:
    file (str): The filepath within 'OUT_DIR/correlations' containing the data to plot
    save_as (str): The name of the png file to save to 'OUT_DIR/plots'.
"""
def plot_correlations(file: str, save_as: str):
    
    # Load areas and merge with lsoa boundaries
    correlations = pd.read_csv(OUT_DIR / "correlations" / file)
    correlations : gpd.GeoDataFrame = lsoas.merge(correlations, on="id")

    # Seperate significant and non-significant clusters
    clusters = correlations[correlations['clustering'] != "not significant"]
    others = correlations[correlations['clustering'] == "not significant"]

    # Plot boundaries of non-significant clusters so we don't lose shape of the UK
    ax = others.boundary.plot(figsize=(8, 10), 
                              linewidth=0.015, 
                              color="black")

    # Plot clusters into 4 categories
    clusters.plot(ax=ax,
                  column="quadrant",
                  cmap="Spectral",
                  scheme='EqualInterval',
                  k=4,
                  edgecolor="black",
                  linewidth=0.015,
                  legend=True,
                  legend_kwds={
                      "labels": ["high-high", "low-high", "low-low", "high-low"],
                      "title": "Clustering"
                  })

    # Turn axis off
    plt.axis("off")
    plt.tight_layout()

    # Save to png
    plt.savefig(OUT_DIR / "plots" / save_as, dpi=300)
    

# Create plot for area ratio
plot_correlations("areas_ratio_correlations.csv", save_as="area_ratio_correlations.png")
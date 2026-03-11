import numpy as np
import pandas as pd
from common.data import OUT_DIR, load_dataset, Datasets

# Load accessibility indicators
areas = pd.read_csv(OUT_DIR / "areas" / "lsoas.csv", index_col=0)
destinations = pd.read_csv(OUT_DIR / "destinations" / "totals.csv", index_col=0)

# Load area boundaries
lsoas = load_dataset(Datasets.CENTRIODS)
regions = load_dataset(Datasets.REGIONS)

# ------------------------
#
#     MEAN (AVERAGE)
#
# ------------------------

# Create blank storage structures
area_agg = pd.DataFrame(columns=areas.columns)
dest_agg = pd.DataFrame(columns=destinations.columns)

# Group lsoas by region
overlay = regions.sjoin(lsoas, predicate="contains")
for index, ((id, name), group) in enumerate(overlay.groupby(["id_left", "name"])):
    contains = group['id_right']
    
    # Calculate mean
    area_agg.loc[index] = [id, name] + list(areas.loc[areas['id'].isin(contains), ~areas.columns.isin(["id", "name"])].mean().values)
    dest_agg.loc[index] = [id, name] + list(destinations.loc[destinations['id'].isin(contains), ~destinations.columns.isin(["id", "name"])].mean().values)
    
# Save mean to file
area_agg.to_csv(OUT_DIR / "areas" / "regional_avg.csv")
dest_agg.to_csv(OUT_DIR / "destinations" / "regional_avg.csv")

# ------------------------
#
#   STANDARD DEVIATION
#
# ------------------------

# Create blank storage structures
area_agg = pd.DataFrame(columns=areas.columns)
dest_agg = pd.DataFrame(columns=destinations.columns)

# Group lsoas by region
overlay = regions.sjoin(lsoas, predicate="contains")
for index, ((id, name), group) in enumerate(overlay.groupby(["id_left", "name"])):
    contains = group['id_right']
    
    # Calculate mean
    area_agg.loc[index] = [id, name] + list(areas.loc[areas['id'].isin(contains), ~areas.columns.isin(["id", "name"])].std().values)
    dest_agg.loc[index] = [id, name] + list(destinations.loc[destinations['id'].isin(contains), ~destinations.columns.isin(["id", "name"])].std().values)
    
# Save mean to file
area_agg.to_csv(OUT_DIR / "areas" / "regional_std.csv")
dest_agg.to_csv(OUT_DIR / "destinations" / "regional_std.csv")

# ------------------------
#
#          RANGE
#
# ------------------------

# Create blank storage structures
area_agg = pd.DataFrame(columns=areas.columns)
dest_agg = pd.DataFrame(columns=destinations.columns)

# Group lsoas by region
overlay = regions.sjoin(lsoas, predicate="contains")
for index, ((id, name), group) in enumerate(overlay.groupby(["id_left", "name"])):
    contains = group['id_right']
    
    # Calculate mean
    area_agg.loc[index] = [id, name] + list(areas.loc[areas['id'].isin(contains), ~areas.columns.isin(["id", "name"])].apply(np.ptp))
    dest_agg.loc[index] = [id, name] + list(destinations.loc[destinations['id'].isin(contains), ~destinations.columns.isin(["id", "name"])].apply(np.ptp))
    
# Save mean to file
area_agg.to_csv(OUT_DIR / "areas" / "regional_range.csv")
dest_agg.to_csv(OUT_DIR / "destinations" / "regional_range.csv")
import os
import pandas as pd
import geopandas as gpd
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from dateutil.relativedelta import relativedelta

PATH = Path(__file__).parent


#--------Process LSOAs with Classifications--------#


print("Merging LSOAs with their classifications:")

# Load LSOA Boundaries
boundaries: gpd.GeoDataFrame = gpd.read_file(PATH / "raw" / "Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4_6453788336260919790.gpkg", use_arrow=True)
print(f"  > Loaded {boundaries.shape[0]} LSOAs")

# Load RUC classifications
classes = pd.read_csv(PATH / "raw" / "Rural_Urban_Classification_(2021)_of_LSOAs_in_EW.csv")
print(f"  > Loaded {classes.shape[0]} corresponding classifications")

# Remove Welsh LSOAs
boundaries = boundaries[~boundaries['LSOA21CD'].str.contains("W")]
classes = classes[~classes['LSOA21CD'].str.contains("W")]
print("  > Removed welsh LSOAs")

# Concatenate RUC classifications
lsoas: gpd.GeoDataFrame = pd.merge(boundaries, classes, on='LSOA21CD', how="outer")
lsoas.reset_index(inplace=True)
print("  > Merged the 2 datasets")

# Drop unwanted columns
lsoas.drop(["LSOA21NMW_x", "BNG_E", "BNG_N", "LAT", "LONG", "GlobalID", "LSOA21NM_y", "LSOA21NMW_y", "RUC21NM", "Urban_rural_flag", "ObjectId"], axis=1, inplace=True)
lsoas.rename({"LSOA21CD": "id", "LSOA21NM_x": "name", "RUC21CD": "ruc"}, axis=1, inplace=True)
print("  > Updated columns")

# Change to Long/Lat Coords
lsoas.to_crs("EPSG:4326", inplace=True)
print("  > Converted to lat/long coordinates")

# Save RUC classification meanings seperately
ruc_def = pd.Series(classes['RUC21NM'].values, index = classes['RUC21CD'])
ruc_def.drop_duplicates(inplace=True)
ruc_def.to_json(PATH / "processed" / "RUC_definitions.json", orient='index', indent=1)
print("  > Saved RUC Definitions to 'processed/RUC_definitions.json'")

# Save as a GeoPackage
lsoas.to_file(PATH / "processed" / "LSOA_Boundaries.gpkg", driver="GPKG", use_arrow=True)
print("  > Saved dataset to 'processed/LSOA_Boundaries.gpkg'")

# Clean up Dataframes
del boundaries, classes, ruc_def, lsoas


#--------Process LSOA Centriods--------#


print("\nProcessing LSOA Centriods:")

# Open existing LSOA centriods
centres: gpd.GeoDataFrame = gpd.read_file(PATH / "raw" / "LSOA_PopCentroids_EW_2021_V4_-3471144733095659889.gpkg", use_arrow=True)
print(f"  > Loaded {centres.shape[0]} LSOAs")

# Remove Welsh LSOAs
centres = centres[~centres['LSOA21CD'].str.contains("W")]
centres.reset_index(inplace=True)
print("  > Removed welsh LSOAs")

# Modify Columns
centres.drop(["GlobalID", "GlobalID_2"], axis=1, inplace=True)
centres.rename({"LSOA21CD": "id"}, axis=1, inplace=True)
print("  > Modified columns")

# Change to Long/Lat Coords
centres.to_crs("EPSG:4326", inplace=True)
print("  > Converted to lat/long coordinates")

# Save to GeoPackage
centres.to_file(PATH / "processed" / "LSOA_Centres.gpkg", driver="GPKG", use_arrow=True)
print("  > Saved to 'processed/LSOA_Centres.gpkg'")

# Clean up dataframes
del centres


#--------Process MSOA Boundaries-----------#


print("\nProcessing MSOA Boundaries:")

# Open existing MSOA Boundaries
msoas: gpd.GeoDataFrame = gpd.read_file(PATH / "raw" / "Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_-6267947188164534400.gpkg", use_arrow=True)
print(f"  > Loaded {msoas.shape[0]} MSOAs")

# Remove Welsh MSOAs
msoas = msoas[~msoas['MSOA21CD'].str.contains("W")]
msoas.reset_index(inplace=True)
print("  > Removed welsh MSOAs")

# Drop unwanted columns
msoas.drop(["MSOA21NMW", "BNG_E", "BNG_N", "LAT", "LONG", "GlobalID"], axis=1, inplace=True)
msoas.rename({"MSOA21CD": "id", "MSOA21NM": "name"}, axis=1, inplace=True)
print("  > Updated columns")

# Change to Long/Lat Coords
msoas.to_crs("EPSG:4326", inplace=True)
print("  > Converted to lat/long coordinates")

# Save as a GeoPackage
msoas.to_file(PATH / "processed" / "MSOA_Boundaries.gpkg", driver="GPKG", use_arrow=True)
print("  > Saved dataset to 'processed/MSOA_Boundaries.gpkg'")

# Clean up Dataframes
del msoas


#--------Process Regions-----------#


print("\nProcessing Region Boundaries:")

# Open existing MSOA Boundaries
regions: gpd.GeoDataFrame = gpd.read_file(PATH / "raw" / "Regions_December_2024_Boundaries_EN_BSC_-5107433749138478884.gpkg", use_arrow=True)
print(f"  > Loaded {regions.shape[0]} regions")

# Drop unwanted columns
regions.drop(["BNG_E", "BNG_N", "LAT", "LONG", "GlobalID"], axis=1, inplace=True)
regions.rename({"RGN24CD": "id", "RGN24NM": "name"}, axis=1, inplace=True)
print("  > Updated columns")

# Change to Long/Lat Coords
regions.to_crs("EPSG:4326", inplace=True)
print("  > Converted to lat/long coordinates")

# Save as a GeoPackage
regions.to_file(PATH / "processed" / "Regions.gpkg", driver="GPKG", use_arrow=True)
print("  > Saved dataset to 'processed/Regions.gpkg'")

# Clean up Dataframes
del regions


#--------Process other destinations-----------#


print("\nCreating a Universal Destinations Dataset:")

# Import previous dataset
sheets = pd.read_excel(PATH / "raw" / "journey-time-statistics-2019-destination-datasets.ods", sheet_name=[1, 2, 3, 4, 5, 6, 7, 8], header=2)
print(f"  > Imported {len(sheets.keys())} existing sheets of destinations")

# Remame fields in GP and Hospitals to match schools
sheets[1].rename({"LSOACode": "urn", "LSOAName": "establishment_name"}, axis=1, inplace=True)
sheets[2].rename({"LSOACode": "urn", "LSOAName": "establishment_name"}, axis=1, inplace=True)
sheets[3].rename({"LSOACode": "urn", "LSOAName": "establishment_name"}, axis=1, inplace=True)
sheets[4].rename({"URN": "urn", "EstablishmentName": "establishment_name"}, axis=1, inplace=True)
sheets[5].rename({"URN": "urn", "EstablishmentName": "establishment_name"}, axis=1, inplace=True)
sheets[6].rename({"URN": "urn", "EstablishmentName": "establishment_name"}, axis=1, inplace=True)
sheets[7].rename({"GP_Code": "urn", "Postcode": "establishment_name"}, axis=1, inplace=True)
sheets[8].rename({"SiteCode": "urn", "SiteName": "establishment_name"}, axis=1, inplace=True)

# Annonate each dataframe with type of destination
sheets[1].insert(4, "type", "small_employment")
sheets[2].insert(4, "type", "medium_employment")
sheets[3].insert(4, "type", "large_employment")
sheets[4].insert(4, "type", "primary_school")
sheets[5].insert(4, "type", "secondary_school")
sheets[6].insert(4, "type", "further_education")
sheets[7].insert(4, "type", "gp")
sheets[8].insert(4, "type", "hospital")

# Join sheets and sort by LSOA Code
dest_df = pd.concat([sheets[1], sheets[2], sheets[3], sheets[4], sheets[5], sheets[6], sheets[7], sheets[8]])
print("  > Created one single dataframe")

# Convert column datatypes
dest_df['urn'] = dest_df['urn'].astype(str)
dest_df['establishment_name'] = dest_df['establishment_name'].astype(str)
dest_df['type'] = dest_df['type'].astype(str)

# Convert to GeoDataframe with Lat/Long Coords
dest_gdf = gpd.GeoDataFrame(dest_df, geometry=gpd.points_from_xy(dest_df['Easting'], dest_df['Northing']), crs="EPSG:27700")
dest_gdf.to_crs("EPSG:4326", inplace=True)
print("  > Converted to lat/long coordinates")

# Clean up Dataframe
dest_gdf.drop(["Easting", "Northing"], axis=1, inplace=True)
print("  > Cleaned un-needed columns")

# Save as a GeoPackage
dest_gdf.to_file(PATH / "processed" / "Destinations.gpkg", driver="GPKG", use_arrow=True)
print("  > Saved to 'processed/Destinations.gpkg'")

# Clean up dataframes
del sheets, dest_df, dest_gdf


#--------Clean GTFS Schedule-----------#


def check_hours(time: str):
    """
    Helper function for checking if a stop-time for a trip is over the maximum allowed time by R5 (72 hours).

    Args:
        time (str): The time to check in the format `hh:mm:dd` as zero-padded integers.
        
    Returns:
        bool: The result of the check.
    """
    hours = int(time.split(":")[0])
    if hours >= 72:
        return True
    else:
        return False

# Create GTFS output folder if it doesn't exist
print("\nCleaning GTFS Schedule for R5:")
if not(os.path.exists(PATH / "processed" / "gtfs")):
    os.mkdir(PATH / "processed" / "gtfs")

# Iterate through each GTFS schedule
for file in os.listdir(PATH / "raw" / "gtfs"):
    save_file = f"{file.replace("itm_", "").replace("_gtfs.zip", "")}_clean.zip"
    print(f"  > Cleaning {file}")

    # Load stop times first to check for non-r5 compatible times (>72 hours)
    with ZipFile(PATH / "raw" / "gtfs" / file, "r") as zip:
        stop_times = pd.read_csv(zip.open("stop_times.txt"))
        print("     > Loaded stop times")

    # Get any misformatted stops
    bad_stops: pd.DataFrame = stop_times.loc[stop_times["departure_time"].map(check_hours)].copy()

    # Get trip IDs
    bad_stops.drop_duplicates("trip_id", inplace=True)
    trip_ids = set(bad_stops["trip_id"].array)

    # Remove any unneeded stop times
    stop_times = stop_times.loc[~stop_times["trip_id"].isin(trip_ids)]
    print(f"     > Removed misformatted stops")

    # Write to new zip file
    with ZipFile(PATH / "processed" / "gtfs" / save_file, "w", compression=ZIP_DEFLATED, compresslevel=3) as out:
        out.writestr("stop_times.txt", stop_times.to_csv(index=False))

    # Clean-up Dataframes
    del stop_times

    # Load trip info
    with ZipFile(PATH / "raw" / "gtfs" / file, "r") as zip:
        trips = pd.read_csv(zip.open("trips.txt"))
        
        # Check if frequencies are also defined as not every region has these
        if "frequencies.txt" in zip.namelist():
            frequencies = pd.read_csv(zip.open("frequencies.txt"))
        else:
            frequencies = None
        print("     > Loaded trip info")

    # Get trip entries
    bad_trips = trips.loc[trips["trip_id"].isin(trip_ids)].copy()

    # Remove trip info
    trips = trips.loc[~trips["trip_id"].isin(trip_ids)]
    
    # Also remove from frequencies if it exists
    if frequencies is not None:
        frequencies = frequencies.loc[~frequencies["trip_id"].isin(trip_ids)]
    print(f"     > Removed {len(trip_ids)} misformatted trips")

    # Add these to zip file
    with ZipFile(PATH / "processed" / "gtfs" / save_file, "a", compression=ZIP_DEFLATED, compresslevel=3) as out:
        out.writestr("trips.txt", trips.to_csv(index=False))
        if frequencies is not None:
            out.writestr("frequencies.txt", frequencies.to_csv(index=False))

    # Clean-up Dataframes
    del frequencies

    # Make sure the any traces of these trips are removed from other files
    with ZipFile(PATH / "raw" / "gtfs" / file, "r") as zip:
        routes = pd.read_csv(zip.open("routes.txt"))
        calendar = pd.read_csv(zip.open("calendar.txt"))
        calendar_dates = pd.read_csv(zip.open("calendar_dates.txt"))
        agencies = pd.read_csv(zip.open("agency.txt"))
        print("     > Loaded route & agency info")

    for trip in bad_trips.itertuples():
        
        # Get agency ID
        agency = routes["agency_id"].loc[routes["route_id"] == trip.route_id].values[0]
        
        # If route has no trips left in the new dataframe, remove it
        if trips["route_id"].value_counts().get(trip.route_id, 0) == 0:
            routes = routes.loc[~routes["route_id"] == trip.route_id]
            print(f"     > Removed route {trip.route_id} since there are no trips left")
        
        # If service has no trips left, remove it
        if trips["service_id"].value_counts().get(trip.service_id, 0) == 0:
            calendar = calendar.loc[~calendar["service_id"] == trip.service_id]
            calendar_dates = calendar_dates.loc[~calendar_dates["service_id"] == trip.service_id]
            print(f"     > Removed service {trip.service_id} since there are no trips left")
            
        # If agency has no routes left, remove it
        if routes["agency_id"].value_counts().get(agency, 0) == 0:
            agencies = agencies.loc[~agencies["agency_id"] == agency]
            print(f"     > Removed agency {agency} since they have no routes left")

    # Add these to zip file
    with ZipFile(PATH / "processed" / "gtfs" / save_file, "a", compression=ZIP_DEFLATED, compresslevel=3) as out:
        out.writestr("routes.txt", routes.to_csv(index=False))
        out.writestr("calendar.txt", calendar.to_csv(index=False))
        out.writestr("calendar_dates.txt", calendar_dates.to_csv(index=False))
        out.writestr("agency.txt", agencies.to_csv(index=False))

    # Clean-up Dataframes
    del trips, routes, calendar, calendar_dates, agencies

    # Load remaining files
    with ZipFile(PATH / "raw" / "gtfs" / file, "r") as zip:
        feed_info = pd.read_csv(zip.open("feed_info.txt"))
        shapes = pd.read_csv(zip.open("shapes.txt"))
        stops = pd.read_csv(zip.open("stops.txt"))
        print("     > Loaded remaining GTFS data")
        
    # Check if feed end-date is too far in the future
    start_date = datetime.strptime(feed_info['feed_start_date'].values.astype(str)[0], "%Y%m%d")
    end_date = datetime.strptime(feed_info['feed_end_date'].values.astype(str)[0], "%Y%m%d")
    if end_date >= datetime(2100, 1, 1):
        print(f"     > Updated feed end-date as it was far in the future ({end_date.year})")
        end_date = start_date + relativedelta(years=1)
        feed_info['feed_end_date'] = [end_date.strftime("%Y%m%d")]
        
    # Add the final files to the zip
    with ZipFile(PATH / "processed" / "gtfs" / save_file, "a", compression=ZIP_DEFLATED, compresslevel=3) as out:
        out.writestr("feed_info.txt", feed_info.to_csv(index=False))
        out.writestr("shapes.txt", shapes.to_csv(index=False))
        out.writestr("stops.txt", stops.to_csv(index=False))
        print(f"     > Saved to 'processed/gtfs/{save_file}'")
# Datasets

This folder contains all datasets involved in the analysis within this project, as well as the code required for preprocessing these datasets before use. Information about each of the datasets and where they were obtained from can be found below:


### Open Street Map (OSM)

An extract of England from Open Street Map provides the road network used by R5 for the routing calculations. It should be downloaded in **protocol buffer format (.pbf)**. The file used for this analysis was downloaded on **20th January 2026** from **Geofabrik** and can be found here: https://download.geofabrik.de/europe/united-kingdom/england.html.


### UK Bus Timetables

A transit schedule is also required by R5 for calculating the bus isochrone. This should be in the **General Transit Feed Specification (GTFS)** format. Information about the Bus timetables in England was obtained from the UK Bus Open Data Service (BODS) on **23rd January 2026**. Files can be found here: https://data.bus-data.dft.gov.uk/timetable/download/.

This project requires the regional extracts, excluding Scotland and Wales. These should be placed into a new subdirectory `data/raw/gtfs`.


### Lower Super Output Areas (LSOAs)

LSOAs are statistical divisons of geographical area in the UK based of the 2021 census. Each comprises of between 400-1200 households and have a population of between 1000-3000 people. The boundaries of these LSOAs were downloaded as a **GeoPackage** from the UK Open Geography Portal, found here: https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2021-boundaries-ew-bsc-v4-2/about.

To increase the accuracy of isochrones, population weighted centriods for each LSOA were obtained as a **GeoPackage** from the Open Geography Portal as well, found here: https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2021-ew-population-weighted-centroids-3/about.

Both files were downloaded on the **8th January 2026**.


### Middle Layer Super Output Areas (MSOAs)

MSOAs are the tier up from LSOAs, with each MSOA comprising of 4-5 LSOAs. Boundaries were obtained as a **GeoPackage** file from the UK Open Geography Portal on **22nd January 2026**, found here: https://geoportal.statistics.gov.uk/datasets/middle-layer-super-output-areas-december-2021-boundaries-ew-bsc-v3-2/about.


### Rural-Urban Classifications

The Office for National Statistics provides a rural-urban classification of each of the LSOAs which is used as part of the analysis. This was obtained as a **CSV** file from the Open Geography Portal on **8th January 2026**, found here: https://geoportal.statistics.gov.uk/datasets/ons::rural-urban-classification-2021-of-lsoas-in-ew/about.


### Destinations

This analysis uses a dataset of destinations in England used by Department of Transport to produce their journey time statistics publications. This can be downloaded in **OpenDocument format (.ods)**, and was obtained from the UK Gov site on **8th January 2026**, found here: https://www.gov.uk/government/publications/journey-time-statistics-guidance.


### Regions

The boundaries of regions within England are required for handling the GTFS files, and aggregating the results at a regional level. These are the 2024 boundaries, obtained as a **GeoPackage** file on **24th January 2026** from the UK Open Geography Portal, found here: https://geoportal.statistics.gov.uk/datasets/ons::regions-december-2024-boundaries-en-bsc-2/about.


### Counties & Unitary Authorities

The boundaries of counties and unitary authorities provide a higher level to agreegrate the results at. These are the 2024 boundaries, obtained as a **GeoPackage** file on **12th March 2026** from the UK Open Geography Portal, found here: https://geoportal.statistics.gov.uk/datasets/ons::counties-and-unitary-authorities-december-2024-boundaries-uk-bsc-1/about.


## Pre-Processing

Before using the datasets, they are cleaned and processed into a more suitable format. Some of the processed needed is:

- Merging the LSOA boundaries with their RUC classification, and updating the columns within the dataframe to only keep the information necessary for the analysis.
- Updating the co-ordinates of the LSOA weighted centriods to Lat/Long, and updating columns.
- Removing all welsh LSOA boundaries and centriods.
- Creating a single destinations Geopackage file, with Lat/Long co-ordinate geometry for the locations.
- Removing invalid data from the GTFS schedule.

These can all be completed by running the *[preprocess.py](preprocess.py)* script. The outputs of this operation are found within the `data/processed` directory.
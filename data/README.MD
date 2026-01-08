## Datasets

This folder contains all datasets required for the analysis within this project. Raw files were obtained on **8th January 2026** from the sources below:

- https://download.geofabrik.de/europe/united-kingdom.html
  - A map of the UK in protocol buffer format (.pdf).*
- https://data.bus-data.dft.gov.uk/timetable/download/
  - Timetable data for all bus services in <u>England</u> in GTFS format.*
- https://www.gov.uk/government/publications/journey-time-statistics-guidance
  - A UK government dataset of destinations in England in OpenDocument format (.ods).
- https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2021-boundaries-ew-bsc-v4-2/about
  - Lower super-output areas (LOSA) regions within England, downloaded as a GeoPackage (.gpkg) file.
- https://geoportal.statistics.gov.uk/datasets/ons::rural-urban-classification-2021-of-lsoas-in-ew/about
  - Rural/Urban classifcations for each LSOA, downloaded as a CSV file.

Some datasets are pre-processed into a more suitable format, and cleaned appropitely using the Python file '*preprocess.py*'. The resulting files can be found in the processed directory.

**Note:**
\* This file is <u>not included</u> in the repository due to GitHub size limits.
# Proof of Concept

This directory contains code used to evaluate how the generation of isochrones works, and how expensive it is computationally. The goal of this to develop a concrete implementation plan for the rest of the research that balances precision with execution time, in order to get the research done within the allocated timeframe.

## full_test.py

This was the intial proof of concept, testing how R5py performs at scale. It creates a transport network covering the whole of the England, and gave insight into the significant memory usage that such a program would require. To run it on my local machine, it required changing the `point_grid_resolution` to 200m.

## small_boundary.py

Once I had understood memory usage, I wanted to experiment further with the output of the isochrone calculation, by saving it to file, and visualising it. To do this, I scaled down the transport network to cover just Devon. This required the use of two new datafiles:

1. A regional OSM extract of Devon in **protocol buffer format** (.pbf), obtained from GeoFarbik on the **15th January 2026**. [^1]
2. Timetable data for all bus services in the South West in **GTFS format**, obtained from the Open Bus Data Service on the **18th January 2026**. [^2]

Due to the smaller transport network, the isochrone calculations were significantly faster, allowing me to experiment with how batching isochrones affected computation time, as well as tweaking the parameters in order to get the most accurate isochrones for modelling my research problem.

## spatial_join.py

Once I've got the isochrones, I will be using spatial joins with the destinations dataset to understand which services lie within an LSOA's isochrone. The code within this file serves as a chance to experiment with this operation, whilst also providing a function that can be used during testing by isolating LSOAs that fall within Devon (~700). To achieve this, another dataset was needed, which defines the territorial boundaries within the UK. It was downloaded as a **GeoPackage** from the UK Open Geography Portal on the **21st January 2026**, and is included in the repository. [^3]

## visualise.py

This was a small file used to generate interactive maps using Folium where I could explore and visualise the isochrones generated in [small-boundary.py](#small-boundarypy). This allowed me to tweak the parameters in the script accordingly until I was happy with the results.

[^1]: https://download.geofabrik.de/europe/united-kingdom/england/devon.html
[^2]: https://data.bus-data.dft.gov.uk/timetable/download/
[^3]: https://geoportal.statistics.gov.uk/datasets/ons::international-territorial-level-2-january-2025-boundaries-uk-buc/about
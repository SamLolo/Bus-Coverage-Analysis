# How Transport Coverage Impacts Access To Equal Opportunities

This code was created as part of my dissertation project, which investigates the accessibility of bus networks across England by using isochrones. Coverage and access to destinations are chosen as indicators of accessibility, and results are compared against driving as a baseline, in order to create ratios which aim to quantify transport disadvantage.

## Running the Code

### Environments

The analysis was carried out using **Python 3.12.12** inside an Anaconda environment, using **Conda 26.1.1**. All packages and versions used are saved within the enclosed `environment.yml` file.

To create & activate the environment:
```shell
conda env create -f environment.yml
conda activate dissertation
```

### Datasets

Due to size contraints on ELE, datasets are __not included__ with the code. More information on all of the datasets used, including when they were obtained and where from, can be found [here](data/README.md).

Before running the code, the main datasets need to be processed. To do this, simply run the Python file:

```shell
cd data
python preprocess.py
cd ..
```

### Proof of Concept

Proof of concept scripts were created first, and can be run like any other Python script. Before running the files, make sure the correct datasets have been copied into the `/poc/data` folder or you will get an error. See [here](poc/README.md) if you're unsure! An example of running one of the files is as follows:

```shell
cd poc
python full_test.py
cd ..
```

More information on each of the proof of concept files, including what they do and why they were created, can be found [here](poc/README.md). Full outputs from all scripts are also included in `/poc/out`.

### Generating Isochrones

From this point on, all Python files share a selection of methods from files within the common directory, and need to be run from the root directory using Python module syntax.

To calculate, you should use the shell scripts located in `/scripts`:

 - `batch.bat` for Windows (run by double clicking it).
 - `batch.sh` for Linux and MacOS (run using `bash batch.sh` in a Terminal).

Isochrone config can be edited inside `config.toml`. To define which MSOAs to calculate, edit the `start_index` and `max_index` at the top of each shell script.

Once all isochrones have been calculated, the next step is to bring them together into 1 file:

```shell
python -m isochrones.concat
python -m isochrones.missing
```

The latter script will output a text file into `/out` which contains any indicies which are missing from the isochrone files. These can be recalculated (on Windows) by runing the `cleanup.bat` file.

Output of all the individual isochrone files from the batches, and some of the text files used to keep track of the computation process for this project can be found in `out/Isochrones`. Additionally, the original GeoPackage files before being polygonised are left here for reference.

### Analysis

Once you have 2 isochrone files: `bus_isochrones_combined.gpkg` and `car_isochrones_combined.gpkg`, you can run the analysis. The area indicator should be calculated first, followed by the destinations indicators, and then the remaining files can be calculated in any order:

```shell
python -m analysis.area
python -m analysis.destinations
python -m spatial_correlation.py
python -m regions.py
python -m counties.py
```

Directories for the output files will be created in `/out` as the code runs.

### Plotting

Once analysis has been completed, plots can be generated using the multitude of scripts found in `/plotting`. Output plots can be found in `out/plots`.

For example:

```shell
python -m plotting.single_isochrone
```

### Evaluation

Evaluation can be completed before or after plotting, but requires isochrone files and outputs from the analysis.

You can view the invalid lsoas and the reasons for them using:

```shell
python -m evaluation.invalid
```

Target LSOAs should be included in the `targets.json` file using their LSOA id. Tests can then by run in any order, but is recommended to run as:

```shell
python -m evaluation.parameters
python -m evaluation.point_to_point
python -m evaluation.snapped_centroid
```

The results of the tests are found in `/out/evaluation`.
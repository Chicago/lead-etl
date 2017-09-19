lead-etl
========

## Introduction

This repository loads a variety of datasets for childhood lead poisoning modeling.

## Implementation
The code for each phase of etl is located in the corresponding subdirectory and is executed using a drakefile.
The output of each phase is contained in a database schema of the same name. 

**input**: Load raw data, see input folder for more details.

**buildings**: Analyze the Chicago buildings shapefile to extract all addresses and group them into buildings and complexes.

**aux**: Process the data to prepare for model building. This includes summarizing and spatially joining datasets.

**dedupe**:Deduplicate the names of children from the blood tests and the WIC Cornerstone database.

**output**: Use the above to create final tables used for exploration, analysis and model feature generation.

## Deployment

### 1.External Dependencies
Install these programs:
- [drake](https://github.com/Factual/drake) (tested with version 1.0.3)
- [mdbtools](https://github.com/brianb/mdbtools) (0.7.1)
- ogr2ogr (2.1.0) with PostgreSQL driver (requires libmq)
- shp2pgsql (2.2.2)
- postgresql-client (9.6.0)

### 2. Libraries
```
sudo apt install libblas-dev liblapack-dev libatlas-base-dev gfortran libhdf5-serial-dev
```

Python modules:
```
pip install -r requirements.txt
```


### 3. Create and configure PostgreSQL database:
Create a database on a PostgreSQL server (tested with version 9.5.4).
Install the PostGIS (2.2.2) and unaccent extensions (requires admin privileges):
```
CREATE EXTENSION postgis;
CREATE EXTENSION unaccent;
```

### 4. Load American Community Survey data:
Use the [acs2ppgsql](https://github.com/dssg/acs2pgsql) tool to load ACS 5-year data for Illinois into the database.
Note that a subset of this data will be imported into the lead pipeline below, so the ACS data may be stored in a separate database from the lead data.

### 5. Configure a profile:
Copy `./lead/example_profile` to `./lead/default_profile` and set the indicated variables.


### 6. Run the ETL workflow by typing `drake`.
To run steps in parallel add the argument `--jobs=N` where `N` is the number of cores to use.

To load data into the pipeline first add the path to the data profile into the `example_profile`. The top-level Drakefile
consists of `%include` statements that bring necessary paths from `example_profile` and the Drakefiles of the sub-directories
`input, buildings, aux, and dedupe`.

# License

See [LICENSE](https://raw.githubusercontent.com/dssg/public-lead/master/LICENSE)

# Contributors
    - Eric Potash (epotash@uchicago.edu)

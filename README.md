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

### 1. Dependencies
#### A) Program dependencies
Install these programs:
- [drake](https://github.com/Factual/drake) (tested with version 1.0.3)
- [mdbtools](https://github.com/brianb/mdbtools) (0.7.1)
- ogr2ogr (2.1.0) with PostgreSQL driver (requires libmq)
- shp2pgsql (2.2.2)
- postgresql-client (9.6.0)

#### B) Library dependencies
[HDF5](https://support.hdfgroup.org/HDF5/) can be installed on Debian-based systems using: `sudo apt-get install libhdf5-serial-dev`, or using conda: `conda install hdf5`.

Python modules can be installed using:
```
pip install -r requirements.txt
```

### 2. Database Setup:
#### A) Create and configure a PostgreSQL database:
Create a database on a PostgreSQL server (tested with version 9.5.4).
Install the PostGIS (2.2.2) and unaccent extensions (requires admin privileges):
```
CREATE EXTENSION postgis;
CREATE EXTENSION unaccent;
```

#### B) Configure a profile file:
Copy `./lead/example_profile` to `./lead/default_profile` and set the indicated variables.


### 3. Test dependencies
Test that the above dependencies were successfull installed by changing by running `lead/check_dependencies.sh`:
```
$ lead/check_dependencies.sh
FOUND: drake, version: Drake now is on version: 1.0.3
FOUND: mdb-tools, version: mdbtools v0.7.1
FOUND: ogr2ogr, version: GDAL 2.1.0, released 2016/04/25
FOUND: shp2pgsql, version: RELEASE: 2.3.3 (r15473)
FOUND: PostgreSQL client, version: psql (PostgreSQL) 9.6.0
FOUND: PostgreSQL server, version: 9.6.0
FOUND: PostgreSQL extension postgis, version: 2.3.3
FOUND: PostgreSQL extension unaccent, version: 1.1
FOUND: Python pandas HDF support
```

### 4. Load American Community Survey data:
Use the [acs2pgsql](https://github.com/dssg/acs2pgsql) tool to load ACS 5-year data for Illinois into the database.
Note that a subset of this data will be imported into the lead pipeline below, so the ACS data may be stored in a separate database from the lead data.

### 5. Run the ETL
Simply change to `lead/` and run `drake`. To run steps in parallel add the argument `--jobs=N` where `N` is the number of cores to use.

# License
[MIT LICENSE](LICENSE)

# Contributors
    - Eric Potash (epotash@uchicago.edu)

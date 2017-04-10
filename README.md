Preventing Childhood Lead Poisoning
====

## Introduction

Lead poisoning is a major public health problem that affects hundreds of thousands of children in the United States every
year. A common approach to identifying lead hazards is to test all children for elevated blood lead levels and then investigate
and remediate the homes of children with elevated tests. This can prevent exposure to lead of future residents,
but only after a child has been irreversibly poisoned. In parternship with the Chicago Department of Public
Health (CDPH),  we have built a model that predicts the risk of a child being poisoned. Our model's risk scores facillitates
an intervention before lead posioning occurs. Using two decades of blood lead level tests, home lead inspections, property value assessments,
and census data, our model allows inspectors to prioritize houses on an intractably long list of potential hazards
and identify children who are at the highest risk. This work has been described by CDPH as pioneering in the use
of machine learning and predictive analytics in public health and has the potential to have a significant impact on both
health and economic outcomes for communities across the US. For a longer overview of the project, see our preliminary results which were written up and
published in the [21st ACM SIGKDD Proceedings](https://github.com/dssg/lead-public/raw/master/kdd.pdf). This project is closely based on previous
[work](https://dssg.uchicago.edu/project/predictive-analytics-to-prevent-lead-poisoning-in-children/) of Joe Brew, Alex Loewi, Subho Majumdar, and Andrew Reece
as part of the 2014 [Data Science for Social Good Summer Fellowship](http://dssg.uchicago.edu).

## Implementation

```
.
├── kdd.pdf
├── lead
│   ├── aux
│   ├── buildings
│   ├── dedupe
│   ├── Drakefile
│   ├── example_profile
│   ├── explore
│   ├── __init__.py
│   ├── input
│   ├── model
│   ├── output
│   └── pilot
├── LICENSE
├── README.md
└── requirements.txt
```
The code for each phase is located in the corresponding subdirectory and is executed using a drakefile.
The output of each phase is contained in a database schema of the same name. Each folder also has a
corresponding README documenting the steps.

**input**: Load raw data, see input folder for more details.

**buildings**: Analyze the Chicago buildings shapefile to extract all addresses and group them into buildings and complexes.

**aux**: Process the data to prepare for model building. This includes summarizing and spatially joining datasets.

**dedupe**:Deduplicate the names of children from the blood tests and the WIC Cornerstone database.

**output**: Generate model features by aggregating the datasets at a variety of spatial and temporal resolutions.

**model**: Use our [drain pipeline](https://github.com/dssg/drain/) to run models in parallel and serialize the results.


## Deployment

### 1.External Dependencies
Install these programs:
- drake (tested with version 1.0.3)
- mdbtools (0.7.1)
- ogr2ogr (2.1.0) with PostgreSQL driver (requires libmq)
- shp2pgsql (2.2.2)
- postgresql-client (9.6.0)

Python modules:
```
pip install -r requirements.txt
```
Clone the drake-psql repository:
```
git clone https://github.com/dssg/drake-psql.git
```

### 2. Create and configure PostgreSQL database:
Create a database on a PostgreSQL server (tested with version 9.5.4).
Install the PostGIS (2.2.2) and unaccent extensions (requires admin privileges):
```
CREATE EXTENSION postgis;
CREATE EXTENSION unaccent;
```

#### 3. Load American Community Survey data:
Use the [acs2ppgsql](https://github.com/dssg/acs2pgsql) tool to load ACS 5-year data for Illinois into the database.
Note that a subset of this data will be imported into the lead pipeline below, so the ACS data may be stored in a separate database from the lead data.

#### 4. Configure a profile:
Copy `./lead/example_profile` to `./lead/default_profile` and set the indicated variables.


#### 5. Run the ETL workflow by typing `drake`.
To run steps in parallel add the argument `--jobs=N` where `N` is the number of cores to use.

To load data into the pipeline first add the path to the data profile into the `example_profile`. The top-level Drakefile
consists of `%include` statements that bring necessary paths from `example_profile` and the Drakefiles of the sub-directories
`input, buildings, aux, and dedupe`.


#### 6. Run models using `drain`.

## Software we use
  - [drake](https://github.com/Factual/drake): workflow management
  - [scikit-learn](http://scikit-learn.org/): machine learning
  - [pandas](http://pandas.pydata.org/): dataframes
  - [pytables](http://www.pytables.org/): HDF files
  - [mdbtools](https://github.com/brianb/mdbtools): Microsoft Access files (tax assessor data)
  - [dedupe](https://github.com/datamade/dedupe): entity deduplication


# License

See [LICENSE](https://raw.githubusercontent.com/dssg/public-lead/master/LICENSE)

# Contributors
    - Eric Potash (epotash@uchicago.edu)

# References
 1. Potash, Eric, Joe Brew, Alexander Loewi, Subhabrata Majumdar, Andrew Reece, Joe Walsh, Eric Rozier, Emile Jorgenson, Raed Mansour, and Rayid Ghani. "Predictive modeling for public health: Preventing childhood lead poisoning." In Proceedings of the 21th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 2039-2047. ACM, 2015.

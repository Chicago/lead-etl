CDPH Childhood Lead Poisoning Model
====

This code models childhood lead poisoning in the city of Chicago.  This project is under development by Eric Potash and Joe Walsh at the University of Chicago's [Center for Data Science and Public Policy](http://dspplab.com) in partnership with the Chicago Department of Public Health. Our first results were published in the [21st ACM SIGKDD Proceedings](https://github.com/dssg/lead-public/raw/master/kdd.pdf).

Closely based on previous [work](https://github.com/dssg/cdph) of Joe Brew, Alex Loewi, Subho Majumdar, and Andrew Reece as part of the 2014 [Data Science for Social Good Summer Fellowship](http://dssg.uchicago.edu).


# The Problem

About 90% of Chicago's housing stock was built before 1978, the year that the Federal Government prohibited almost all lead from paint.  Lead poisoning affects neurological development, leading to lower IQs, increased need for special education, lower wages, and increased crime.  Lead has the greatest effect during the first two years of the child's life, but many kids don't get tested until later.


# The Solution

The pipeline consists of three phases which are summarized below. The code for each phase is located in the corresponding subdirectory. The output of each phase is contained in a database schema of the same name.

##input
Here we preprocess and import our data into the database.
CDPH provided us with two databases about lead:
 - Blood Lead Level Tests
 - Home Inspections

We supplemented that data with the following public datasets:
 - [Chicago addresses](https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Address-Point-Chicago/jev2-4wjs)
 - [Cook County Assessor Data](http://www.cookcountyassessor.com/)
 - [Building Footprints](https://github.com/Chicago/osd-building-footprints)
 - [Build Permits](https://data.cityofchicago.org/Buildings/Building-Permits/ydr8-5enu)
 - [Building Violations](https://data.cityofchicago.org/Buildings/Building-Violations/22u3-xenr)
 - [American Community Survey](http://factfinder.census.gov/faces/nav/jsf/pages/index.xhtml)

##aux
Here we process the data to prepare for model building. That includes summarizing and spatially joining datasets.

##output
Here we generate model features by aggregating the datasets at a variety of spatial and temporal resolutions.

##model
Here we use our [drain pipeline](https://github.com/dssg/drain/) to run run models in parallel and serialize the results.


# Running the model
We run the workflow using drake. Specify the following environment variables in the `lead/default_profile` file:

```
# Postgresql databse connection information
PGHOST=
PGDATABASE=
PGUSER=
PGPASSWORD=

ASSESSOR_FILE= # Cook County Tax Assessor MDB file
CURRBLLSHORT_FILE= # Current blood lead levels CSV file
M7_FILE= # Old blood lead levels CSV file
INSPECTIONS_FILE= # Inspections CSV file
CORNERSTONE_DIR= # Directory containing Cornerstone DBF files
```

## Install software
  - [drake](https://github.com/Factual/drake)
  - [mdbtools](https://github.com/brianb/mdbtools): a command-line tool that reads Microsoft Access files, which is useful for reading the property-assessment data 

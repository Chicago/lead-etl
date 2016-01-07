#!/bin/bash

git clone https://github.com/Chicago/osd-building-footprints
unzip data/Buildings.zip

ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:"host=$PGHOST user=$PGUSER password=$PGPASSWORD dbname=$PGDATABASE" Buildings.json -lco "schema=input" -nln buildings

# fix building condition
psql -c "
	UPDATE input.buildings SET bldg_condi = 'UNINHABITABLE'
	WHERE bldg_condi = 'UNNHABITABLE'
"

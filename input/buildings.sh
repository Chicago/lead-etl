#!/bin/bash

file=$1

ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:"host=$PGHOST user=$PGUSER password=$PGPASSWORD dbname=$PGDATABASE" $file -lco "schema=input" -nln buildings

# fix building condition
psql -c "
	UPDATE input.buildings SET bldg_condi = 'UNINHABITABLE'
	WHERE bldg_condi = 'UNNHABITABLE'
"

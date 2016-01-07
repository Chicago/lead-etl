#!/bin/bash

file="/glusterfs/users/erozier/data/inspections_geocoded.csv"

psql -c "
    DROP TABLE IF EXISTS source.inspections_geocoded; 

    CREATE TABLE source.inspections_geocoded (
	n integer, X integer, addr_id integer primary key,
        init_date integer, comply_date integer,
        interior boolean, exterior boolean, clean boolean,
        address text, apt text,
        addr_num text, direction integer, streetname text,
        streettype integer, addr_full_2 text,
        census_block text, XCOORD decimal, YCOORD text,
        STATUS1 text, STATUS2 text,
        civis_latitude decimal, civis_longitude decimal,
        civis_geocode_rating decimal, civis_statefp decimal,
        civis_countyfp decimal, civis_tractce decimal, civis_blkgrpce decimal,
        civis_blockce decimal, civis_cousubfp decimal, civis_placefp decimal,
        civis_elsdlea decimal, civis_scsdlea decimal, civis_unsdlea decimal,
        civis_cd111fp decimal, civis_sldust decimal, civis_sldlst decimal,
        civis_csafp decimal, civis_cbsafp decimal, civis_metdivfp decimal,
	latlong text);"

# census_block and YCOORD are type text
# because occasionally they are an address and "VALID", respectively

# replace NA with empty (null)

awk 'BEGIN {FS=OFS=","} {
	for (i=1;i<=NF;i++){ 
	   if ($i=="NA") {$i = ""}
	} 
	print $0;
    };' $file | \
    PGPASSWORD=$password \
    psql -h $host -U $user -d $db -c \
    "\COPY source.inspections_geocoded FROM STDIN WITH CSV HEADER"

#!/bin/bash

file=$1

psql -c "
    DROP TABLE IF EXISTS input.currbllshort; 
    
    CREATE TABLE input.currbllshort (
	currbllshort_id int,
	sequential_id_sent_to_stellar int, 
        bll int, 
	apt text,
	city text,
        first_name text,
	last_name text,
	mi text,
        sample_type char,
        sex char,
        street text,
        lab_id text,
        address text,
        ethnicity text,
        race text,
        house_number text,
        billing_id text,
        census_tract_id text,
        othtrannum text,
        phone text,
        spec_id int,
        zip text,
        analysis_date date,
        date_of_birth date,
        reported_date date,
        sample_date date,
        provider_id text,
        clean_name text,
        clean_birth_date date,
        clean_birth_month text,
        clean_birth_day text,
        clean_birth_year text,
        clean_birth_text text,
        geocode_building text,
        geocode_tract text,
        clean_address text,
        clean_zip text,
        geocode_community_area text,
        clean_primary_dir text,
        clean_root_name text,
        clean_street_type text,
        clean_unit text,
        clean_unit_type text,
        geocode_ward text,
        geocode_unique text,
        clean_fname text,
        clean_lname text,
        clean_namedob text,
        geocode_bldg_grid text,
        geocode_census_block_2010 text,
        geocode_census_block_2000 text,
        geocode_ward_2015 text,
        geocode_full_addr text,
        geocode_house_low text,
        geocode_house_high text,
        geocode_pre text,
        geocode_street_name text,
        geocode_street_type text,
        geocode_sufdir text,
        geocode_xcoord decimal,
        geocode_ycoord decimal,
        geocode_status1 text,
        geocode_status2 text
        );"

PGCLIENTENCODING="latin1" \
    psql -c \
    "\COPY input.currbllshort FROM STDIN WITH CSV HEADER;
    ALTER TABLE input.currbllshort ADD COLUMN id SERIAL PRIMARY KEY;"

# the original id in currbllshort is sometimes null so create a new one


#!/bin/bash

psql -c "
    DROP TABLE IF EXISTS input.m7; 

    CREATE TABLE input.m7 (cleaned_address text, 
        xcoord text, ycoord text,
        id text, first_name text, last_name text, sex char,
        date_of_birth text, address text, apt text, city text,
        bll text, sample_type char, sample_date text, data_source integer, lab text,
        dbod text, birthcheck text, 
        geocode_full_addr text, geocode_house_low text, geocode_house_high text,
        geocode_pre text, geocode_street_name text, geocode_street_type text, geocode_sufdir text, geocode_xcoord text, geocode_ycoord text, geocode_status1 text, geocode_status2 text);"

cat "$1" | PGCLIENTENCODING="latin1" psql -c "\COPY input.m7 FROM STDIN WITH CSV HEADER;"

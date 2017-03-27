#!/bin/bash

psql -c "
DROP TABLE IF EXISTS cornerstone.addresses;

CREATE TABLE cornerstone.addresses (
    address text, 
    zip text, 
    city text, 
    ogc_fids int[],

    geocode_full_addr text, geocode_house_low text, geocode_house_high text, geocode_pre text, geocode_street_name text, geocode_street_type text, geocode_sufdir text, geocode_xcoord text, geocode_ycoord text, geocode_status1 text, geocode_status2 text

);"

psql -c "\COPY cornerstone.addresses FROM $1 WITH CSV HEADER"

psql -c "ALTER TABLE cornerstone.addresses ADD COLUMN geocode_address text;

    update cornerstone.addresses
    set geocode_address =  geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || geocode_street_type
    where city ilike 'CH%';"

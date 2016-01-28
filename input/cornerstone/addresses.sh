#!/bin/bash

psql -c "
DROP TABLE IF EXISTS cornerstone.addresses;

CREATE TABLE cornerstone.addresses (
    ogc_fids int[], addr_ln1_t text, addr_zip_n text, addr_cty_t text, full_addr text, house_low text, house_high text, pre text, street_name text, street_type text, sufdir text, xcoord text, ycoord text, status1 text, status2 text

);"

psql -c "\COPY cornerstone.addresses FROM $1 WITH CSV HEADER"

psql -c "
ALTER TABLE cornerstone.addresses ADD COLUMN address text;

update cornerstone.addresses
    set address =  house_low || ' ' || pre || ' ' || street_name || ' ' || street_type;
"

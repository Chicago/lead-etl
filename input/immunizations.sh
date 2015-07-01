#!/bin/bash

psql -c "

drop table if exists input.immunizations;

create table input.immunizations (
    first_name text,
    last_name text,
    date_of_birth date,
    sex text,
    address text,
    address2 text,
    city text,
    zip text,
    antigent text, 
    shot_date date
);
"

cut -d, -f11-20 $1 | psql -c "\copy input.immunizations from stdin with csv header"

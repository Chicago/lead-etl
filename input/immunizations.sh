#!/bin/bash

psql -c "

drop table if exists input.immunizations;

create table input.immunizations (
    first_name text,
    last_name text,
    date_of_birth date,
    sex char,
    address text,
    address2 text,
    city text,
    zip text,
    antigent text, 
    shot_date date
);
"

psql -c "\copy input.immunizations from '$1' with csv header"

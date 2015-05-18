#!/bin/bash
file=$1

psql -c "
    DROP TABLE IF EXISTS input.m7; 

    CREATE TABLE input.m7 (cleaned_address text, 
        xcoord text, ycoord text,
        id integer primary key, first_name text, last_name text, sex char,
        date_of_birth date, address text, apt text, city text,
        bll int, sample_type char, sample_date date, data_source integer, lab text,
        dbod date, birthcheck integer);"

PGCLIENTENCODING="latin1" \
psql -c \
"\COPY input.m7 FROM '$file' WITH CSV HEADER;"

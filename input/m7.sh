!/bin/bash
file=$1

psql -c "
    DROP TABLE IF EXISTS input.m7; 

    CREATE TABLE input.m7 (cleaned_address text, 
        xcoord decimal, ycoord decimal,
        id integer primary key, first_name text, last_name text, sex char,
        date_of_birth date, address text, apt text, city text,
        bll int, sample_type char, sample_date date, data_source integer, lab text,
        dbod date, birthcheck integer);"


# replace ERROR and -1 in XCOORD and YCOORD columns with empty (null)
awk 'BEGIN {FS=OFS=","} {
        if ($2=="ERROR" || $2=="-1") {$2=""};
        if ($3=="ERROR" || $3=="-1") {$3=""};
        print $0; }' $file | \
    PGCLIENTENCODING="latin1" \
    psql -c \
    "\COPY input.m7 FROM STDIN WITH CSV HEADER;"
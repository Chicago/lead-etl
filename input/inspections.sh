file=$1

psql -v ON_ERROR_STOP=1 -c "
    DROP TABLE IF EXISTS input.inspections; 

    CREATE TABLE input.inspections (
	addr_id integer,
	comply1 integer,
	comply_date1 integer,
	initial1 integer,
	init_date1 integer,
	hazard_int boolean,
	hazard_ext boolean,
	CLO integer,
	comply_date2 date,
	init_date2 date,
	initial2 integer,
	comply2 integer,
	address text,
	apt text,
	addr_num text,
	direction integer,
	street_name text,
	street_type integer,
	cleaned_address boolean
	);"

# replace NA with empty (null)

awk 'BEGIN {FS=OFS=","} {
	if ($6=="I") $6="1,0";
	else if ($6=="E") $6="0,1";
	else if ($6=="N") $6="0,0";
	else if ($6=="B") $6="1,1";
	else $6=",";
	print $0;
    };' "$file" | \
    psql -v ON_ERROR_STOP=1 -c \
    "\COPY input.inspections FROM STDIN WITH CSV HEADER"

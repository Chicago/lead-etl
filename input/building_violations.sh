#!/bin/bash

file=$1

psql -c "
drop table if exists input.building_violations;

create table input.building_violations (
	id integer not null, 
	violation_last_modified_date date not null, 
	violation_date date not null, 
	violation_code varchar(9) not null, 
	violation_status varchar(8) not null, 
	violation_status_date date, 
	violation_description varchar(30), 
	violation_location varchar(242), 
	violation_inspector_comments varchar(3869), 
	violation_ordinance varchar(807), 
	inspector_id varchar(9) not null, 
	inspection_number integer not null, 
	inspection_status varchar(6) not null, 
	inspection_waived varchar(1) not null, 
	inspection_category varchar(12) not null, 
	department_bureau varchar(26) not null, 
	address varchar(50) not null, 
	property_group integer not null, 
	ssa integer, 
	latitude float, 
	longitude float, 
	location varchar(39)
);"

sed 's/, ,/,,/g' $file | psql -c "\copy input.building_violations from stdin with csv header;"

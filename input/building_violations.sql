drop table if exists input.building_violations;

create table input.building_violations (
	id integer not null, 
	violation_last_modified_date date not null, 
	violation_date date not null, 
	violation_code text not null, 
	violation_status text not null, 
	violation_status_date date, 
	violation_description text, 
	violation_location text, 
	violation_inspector_comments text, 
	violation_ordinance text, 
	inspector_id text not null, 
	inspection_number integer not null, 
	inspection_status text not null, 
	inspection_waived text not null, 
	inspection_category text not null, 
	department_bureau text not null, 
	address text not null, 
	property_group integer not null, 
	ssa integer, 
	latitude float, 
	longitude float, 
	location text
);

\copy input.building_violations from 'data/building_violations.csv' with csv header;

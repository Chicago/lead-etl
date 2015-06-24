drop table if exists buildings.original_addresses;

create table buildings.original_addresses as (
	select orig_bldg_, generate_series(f_add1,t_add1,2) || ' ' || pre_dir1 || ' ' || st_name1 || ' ' || st_type1 as address,
	geom, edit_date
	from buildings.original_buildings
);

alter table buildings.original_addresses add column id serial primary key;

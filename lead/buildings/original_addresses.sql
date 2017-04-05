drop table if exists buildings.original_addresses;

create table buildings.original_addresses as (
        -- need to trim address because when st_type1 is empty don't want trailing space
	select orig_bldg_, trim(generate_series(f_add1::int,t_add1::int,2) || 
                ' ' || pre_dir1 || ' ' || st_name1 || ' ' || st_type1) as address,
	geom, edit_date, gid
	from buildings.original_buildings
);

alter table buildings.original_addresses add column id serial primary key;

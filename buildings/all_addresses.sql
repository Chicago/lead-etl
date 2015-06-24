create table buildings.all_addresses as (
	select orig_bldg_, generate_series(f_add1,t_add1,2) || ' ' || pre_dir1 || ' ' || st_name1 || ' ' || st_type1 as address,
	st_transform(st_setsrid(st_point(x_coord,y_coord),3435), 4326) as geom,
	from input.buildings
);
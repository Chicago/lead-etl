drop table if exists aux.inspections;

create table aux.inspections as (
	select addr_id, 
	hazard_int,
	hazard_ext,
	init_date2 init_date,
	comply_date2 comply_date
	FROM input.inspections
	WHERE init_date2 is not null OR comply_date2 is not null
);

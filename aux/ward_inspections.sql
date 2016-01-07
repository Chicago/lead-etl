drop table if exists aux.ward_inspections;

create table aux.ward_inspections as (
	select ward_id, date_part('year', greatest(comply_date,init_date)) as year,
		1 as years, 
		count(*) as count,
		sum(hazard_int::int) hazard_int_count,
		sum(hazard_ext::int) hazard_ext_count,
		sum(hazard_int::int)::decimal/count(*) hazard_int_ratio,
		sum(hazard_ext::int)::decimal/count(*) hazard_ext_ratio
	from aux.inspections i 
	join aux.inspection_addresses ia on i.addr_id = ia.inspection_addr_id
	join aux.addresses a on ia.address_id = a.id
	group by ward_id, date_part('year', greatest(comply_date,init_date))
);
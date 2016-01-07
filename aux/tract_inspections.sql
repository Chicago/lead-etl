drop table if exists aux.tract_inspections;

create table aux.tract_inspections as (
	with address_counts as (
		select census_tract_id, count(*) as census_tract_count from aux.addresses group by census_tract_id
	)

	select census_tract_id, date_part('year', greatest(comply_date,init_date)) as year,
		count(*) as count,
		sum(hazard_int::int) hazard_int_count,
		sum(hazard_ext::int) hazard_ext_count,
		sum(hazard_int::int)::decimal/count(*) hazard_int_ratio,
		sum(hazard_ext::int)::decimal/count(*) hazard_ext_ratio,
		sum((comply_date is not null)::int) as compliance_count,
		sum((comply_date is not null)::int)::decimal/count(*) as compliance_ratio,
		avg(comply_date - init_date) as avg_init_to_comply_days,
		count(*)::decimal/max(census_tract_count) as pct_inspected -- max is redundant, they are all the same
	from aux.inspections i 
	join aux.inspection_addresses ia on i.addr_id = ia.inspection_addr_id
	join aux.addresses a on ia.address_id = a.id
	join address_counts ac using (census_tract_id)
	group by census_tract_id, date_part('year', greatest(comply_date,init_date))
);

drop table if exists aux.address_inspections;

create table aux.address_inspections as (

select t.id test_id, 
	count(*) count,
	not bool_or(not i.hazard_int) hazard_int, -- False iff. there was ever NO hazard found
    not bool_or(not i.hazard_ext) hazard_ext,
	sum(hazard_int::int) hazard_int_count,
	sum(hazard_ext::int) hazard_ext_count,
	min(i.init_date) as min_init_date,  -- earliest init date
	min(i.comply_date) as min_comply_date, -- earliest comply date
	max(i.init_date) as max_init_date,  -- last init date
	max(i.comply_date) as max_comply_date -- last comply date
from aux.tests_geocoded t
join aux.inspection_addresses ig on t.address_id = ig.address_id
join aux.inspections i on ig.inspection_addr_id = i.addr_id
	and (i.init_date < t.sample_date and i.comply_date < t.sample_date)
group by t.id

);

alter table aux.address_inspections add primary key(test_id);

drop table if exists aux.test_inspections;

create table aux.test_inspections as (

select t.id test_id, 
	count(*) count,
	not bool_or(not i.hazard_int) hazard_int,
    not bool_or(not i.hazard_ext) hazard_ext,
	min(i.init_date) as init_date,  -- earliest init date
	min(i.comply_date) as comply_date -- earliest comply date
from input.tests t
join aux.test_addresses tg on t.id = tg.test_id
join aux.inspection_addresses ig on tg.address_id = ig.address_id
join aux.inspections i on ig.inspection_addr_id = i.addr_id
	and (i.init_date < t.sample_date or i.comply_date < t.sample_date) 
group by t.id

);
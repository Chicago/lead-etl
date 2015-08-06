drop table if exists output.inspections;

create table output.inspections as (
	select i.*, 
	ia.address_id
	from aux.inspections i
	join aux.inspection_addresses ia
	on i.addr_id = ia.inspection_addr_id
);

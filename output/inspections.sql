drop table if exists output.inspections;

create table output.inspections as (
	select i.*, 
	a.id address_id, a.community_area_id, a.ward_id, a.census_tract_id, ca.complex_id
	from aux.inspections i
	join aux.inspection_addresses ia
	on i.addr_id = ia.inspection_addr_id
	join aux.addresses a on ia.address_id = a.id
        join aux.complex_addresses ca on ca.address_id = a.id
);

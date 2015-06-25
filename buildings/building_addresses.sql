drop table if exists buildings.building_addresses;

create table buildings.building_addresses as (

select a.id address_id, bc.id1 as building_id 
from buildings.addresses a join buildings.original_addresses oa using (address) 
join buildings.building_components bc on bc.id2 = oa.ogc_fid
group by a.id, bc.id1
);


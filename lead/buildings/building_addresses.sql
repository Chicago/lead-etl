drop table if exists buildings.building_addresses;

create table buildings.building_addresses as (

select a.id address_id, bc.id1 as building_id
from buildings.addresses a join buildings.building_components bc
on a.gid = bc.id2
);

alter table buildings.building_addresses add unique(address_id);

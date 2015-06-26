drop table if exists buildings.buildings;

create table buildings.buildings as (
    select distinct building_id as id from buildings.building_addresses
)

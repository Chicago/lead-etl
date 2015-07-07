DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

select a.id address_id, a.address, ca.building_id, ca.complex_id,
    cast(a.census_tract_id as double precision), cast(a.census_block_id as double precision), a.ward_id, a.community_area_id,
    st_y(a.geom) address_lat,
    st_x(a.geom) address_lng
from aux.addresses a join aux.complex_addresses ca on a.id = ca.address_id);

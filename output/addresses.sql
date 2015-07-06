DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

select a.id address_id, 
    a.census_tract_id, a.census_block_id, a.ward_id, a.community_area_id,
    st_y(a.geom) address_lat,
    st_x(a.geom) address_lng
from aux.addresses a);

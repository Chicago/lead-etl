DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

with tested_addresses as (
    select address_id from aux.test_addresses group by address_id
),

residential_complexes as (
    select complex_id
    from aux.addresses a 
    left join aux.complex_addresses ca on ca.address_id = a.id
    left join aux.assessor_summary using (address)
    group by complex_id having sum(residential) > 0
)

select a.id address_id, a.address, ca.building_id, ca.complex_id,
    cast(a.census_tract_id as double precision), cast(a.census_block_id as double precision), a.ward_id, a.community_area_id,
    st_y(a.geom) address_lat,
    st_x(a.geom) address_lng,
    (rc.complex_id is not null) or (ta.address_id is not null) as address_residential
from aux.addresses a join aux.complex_addresses ca on a.id = ca.address_id
left join residential_complexes rc using (complex_id)
left join tested_addresses ta using(address_id)

);

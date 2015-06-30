DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

--with test_addresses as (
--    select distinct (address_id) address_id from aux.test_addresses
--)

select a.id address_id, 
--	(ta.address_id is not null or ass.residential) as residential,
	a.census_tract_id, a.ward_id, a.community_area_id,
    st_y(a.geom) address_lat,
    st_x(a.geom) address_lng

--	bd.address is null address_building_null,
--	bd.year_built address_building_year,
--    bd.year_built <= 1978 as address_building_pre1978,
--    bd.bldg_condi address_building_condition,
--    bd.units address_building_units,
--    bd.stories address_building_stories,
--    bd.vacant address_building_vacant,

--	ass.address is null address_assessor_null,
--    ass.total_value address_assessor_total_value,
--    ass.age address_assessor_age
    
from aux.addresses a 
--left join test_addresses ta on a.id = ta.address_id
--    left join aux.assessor_summary ass using(address)
--    left join aux.buildings_summary bd using(address)
);

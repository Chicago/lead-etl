DROP TABLE IF EXISTS aux.addresses;

CREATE TABLE aux.addresses(id serial primary key, address text unique not null, geom geometry, census_tract_id text, census_block_id text, ward_id int, community_area_id int, source text);

-- load addresses from geocoded tests
INSERT INTO aux.addresses (address, geom, census_tract_id, census_block_id, ward_id, community_area_id, source) (
with cleaned_addresses as (
	select distinct on (geocode_full_addr) geocode_full_addr address,
	st_transform(st_setsrid(st_point(nullif(geocode_xcoord,-1),nullif(geocode_ycoord,-1)),3435), 4326) as geom,
	nullif(geocode_census_block_2010, ' ') as census_block_id,
	nullif(geocode_ward_2015, ' ')::int as ward_id,
	nullif(regexp_replace(geocode_community_area, '[^0-9]', '', 'g'), '')::int as community_area_id
	from input.currbllshort 
	where nullif(geocode_full_addr, ' ') is not null order by geocode_full_addr
)
	select a1.address, a1.geom, 
	substring(a1.census_block_id for 11), substring(a1.census_block_id from 12), 
	a1.ward_id, a1.community_area_id, 'tests'  
	from cleaned_addresses a1 
	left join aux.addresses a2 using (address) where a2.address is null
);

-- load addresses from chicago address table
INSERT INTO aux.addresses (address, geom, source) (
        SELECT DISTINCT ON (cmpaddabrv) a.cmpaddabrv, a.geom,
        'addresses'
        FROM input.addresses a
	left join aux.addresses a2 on a.cmpaddabrv = a2.address where a2.address is null
	and a.cmpaddabrv is not null
        ORDER BY cmpaddabrv, edittime desc
);

update aux.addresses a
SET census_tract_id = 
-- get_tract(a.geom, 'tract_id');
-- chicago tracts table lookup is faster! does postgis tiger not use a spatial index?
(select c.geoid10 from input.census_tracts c where st_contains(c.geom, a.geom) limit 1)
WHERE census_tract_id is null;

UPDATE aux.addresses a
SET ward_id = (select w.ward::int from input.wards w where st_contains(w.geom, a.geom) and w.ward != 'OUT' limit 1)
WHERE ward_id is null;


UPDATE aux.addresses a
SET community_area_id = (select c.area_numbe::int from input.community_areas c where st_contains(c.geom, a.geom) limit 1)
WHERE community_area_id is null;

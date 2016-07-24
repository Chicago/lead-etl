DROP TABLE IF EXISTS aux.addresses;

CREATE TABLE aux.addresses(address_id serial primary key, address text unique not null, geom geometry, census_tract_id text, census_block_id text, ward_id int, community_area_id int, source text);

-- load addresses from geocoded tests
INSERT INTO aux.addresses (address, geom, census_tract_id, census_block_id, ward_id, community_area_id, source) (

-- first get all addresses and areas from currbllshort
-- and addresses from m7 and cornerstone
-- only take addresses where city starts with 'CH'-- Chicago geocoder doesn't work outside of Chicago:w
with all_addresses as (
    select 
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || clean_street_type
            as address, 
        geocode_xcoord, geocode_ycoord, '17031' || nullif(geocode_census_block_2010, ' ') as census_block_id,
        CASE WHEN geocode_ward ~ E'^\\d+$' THEN geocode_ward::int END ward_id,
        CASE WHEN geocode_community_area ~ E'^\\d+$' THEN geocode_community_area::int END community_area_id,
        'currbllshort' as source
    from input.currbllshort
    WHERE city ilike 'CH%'
    UNION ALL
    select
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || geocode_street_type
            as address, 
        geocode_xcoord::decimal, geocode_ycoord::decimal, null, null, null, 'm7'
    from input.m7
    WHERE city ilike 'CH%'
    UNION ALL
    select
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || geocode_street_type
            as address, 
        geocode_xcoord::decimal, geocode_ycoord::decimal, null, null, null, 'cornerstone'
    from cornerstone.addresses
    WHERE city ilike 'CH%' and geocode_xcoord != 'ERROR' and geocode_ycoord != 'ERROR'
),
addresses as (
	select distinct on (address) address,
	st_transform(st_setsrid(st_point(geocode_xcoord,geocode_ycoord),3435), 4326) as geom,
        census_block_id, ward_id, community_area_id, source
	from all_addresses
	where address is not null
        and geocode_xcoord != -1 and geocode_ycoord != -1
        order by address, (census_block_id is null) asc
)
	select address, geom, 
	substring(census_block_id for 11), census_block_id, 
	ward_id, community_area_id, source
	from addresses
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

-- load addresses from chicago buildings footprint
INSERT INTO aux.addresses (address, geom, source) (
        SELECT a.address, a.geom, 'buildings'
        FROM buildings.addresses a
        left join aux.addresses a2 using(address) where a2.address is null
);

-- set census tract and block ids
with address_blocks as (
    select a.address_id, (select c.geoid10 from input.census_blocks c where st_contains(c.geom, a.geom) limit 1)
    from aux.addresses a
    where a.census_tract_id is null or a.census_block_id is null
)
update aux.addresses a
set
    census_tract_id = substring(geoid10 for 11),
    census_block_id = geoid10
FROM address_blocks ab
WHERE a.address_id = ab.address_id;

-- ward id
UPDATE aux.addresses a
SET ward_id = (select w.ward::int from input.wards w where st_contains(w.geom, a.geom) and w.ward != 'OUT' limit 1)
WHERE ward_id is null;

-- community area id
UPDATE aux.addresses a
SET community_area_id = (select c.area_numbe::int from input.community_areas c where st_contains(c.geom, a.geom) limit 1)
WHERE community_area_id is null;

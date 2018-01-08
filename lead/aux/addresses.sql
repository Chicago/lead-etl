DROP TABLE IF EXISTS aux.addresses;

CREATE TABLE aux.addresses(address_id serial primary key, 
    address text unique not null, geom geometry not null, 
    census_tract_id text, census_block_id text, 
    ward_id int, community_area_id int, zip_code int, 
    source text not null
);

-- load addresses from geocoded tests
INSERT INTO aux.addresses (address, geom, source) (

-- first get all addresses and areas from currbllshort
-- and addresses from m7 and cornerstone
-- only take addresses where city starts with 'CH'-- Chicago geocoder doesn't work outside of Chicago
with all_addresses as (
    select 
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || clean_street_type as address,
        geocode_xcoord, geocode_ycoord, 
        'currbllshort' as source
    from input.currbllshort
    WHERE city ilike 'CH%'
    UNION ALL
    select
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || geocode_street_type as address,
        geocode_xcoord::decimal, geocode_ycoord::decimal,
        'm7'
    from input.m7
    WHERE city ilike 'CH%'
    UNION ALL
    select
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || geocode_street_type as address,
        geocode_xcoord::decimal, geocode_ycoord::decimal, 
        'cornerstone'
    from cornerstone.addresses
    WHERE city ilike 'CH%' and geocode_xcoord != 'ERROR' and geocode_ycoord != 'ERROR'
)

select distinct on (address) address,
    st_transform(st_setsrid(st_point(geocode_xcoord,geocode_ycoord),3435), 4326) as geom,
    source
from all_addresses
where address is not null and
    geocode_xcoord != -1 and geocode_ycoord != -1
order by 1

);

-- load addresses from chicago buildings footprint
INSERT INTO aux.addresses (address, geom, source) (
        SELECT a.address, st_centroid(a.geom), 'buildings'
        FROM buildings.addresses a
        left join aux.addresses a2 using(address) where a2.address is null
);

-- load addresses from assessor join parcels
CREATE TEMP TABLE pin_address AS (
    select substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix as address,
    substring("PIN" for 10) as pin10
    from input.assessor
    where city = 'CHICAGO'
);

CREATE TEMP TABLE address_geom AS (
    select address, st_centroid(st_collect(geom)) as geom
    from pin_address
    join input.parcels using (pin10)
    where address is not null
    group by 1
);

INSERT INTO aux.addresses (address, geom, source) (
        SELECT a.address, a.geom, 'parcels'
        FROM address_geom a
	left join aux.addresses a2 using (address)
        where a2.address is null
);

-- load addresses from building violations
INSERT INTO aux.addresses (address, geom, source) (
    select distinct on(address)
    address, st_setsrid(st_point(longitude, latitude), 4326), 
        'violations'
    from input.building_violations
    left join aux.addresses a2 using (address)
    where a2.address is null
        and longitude is not null and latitude is not null
    order by 1
);

-- load addresses from building permits
INSERT INTO aux.addresses (address, geom, source) (
    with permit_addresses as (
        select street_number || ' ' || street_direction || ' ' || street_name || ' ' || suffix address,
            st_setsrid(st_point(longitude, latitude),4326) as geom
        from input.building_permits
    )
    select distinct on (address)
    a.address, a.geom, 'permits'
    from permit_addresses a
    left join aux.addresses a2 using (address)
    where a2.address is null
    and a.address is not null and a.geom is not null
    order by 1
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

-- zip code
UPDATE aux.addresses a
SET zip_code = (select z.zip::int from input.zip_codes z where st_contains(z.geom, a.geom) limit 1)
WHERE zip_code is null;

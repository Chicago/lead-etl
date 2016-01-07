drop table if exists aux.ward_tracts;

create table aux.ward_tracts as (
    select t.geoid10 census_tract_id, w.ward::int ward_id,
    st_area(st_intersection(w.geom, t.geom))/st_area(t.geom) as area
    from input.wards w join input.census_tracts t on st_intersects(w.geom, t.geom)
    where w.ward != 'OUT'
);
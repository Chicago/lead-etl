DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

select a.id address_id, (ta.address_id is not null or ass.residential)::int as residential,
    a.census_tract_id, a.ward_id
    from aux.addresses a left join aux.test_addresses ta on a.id = ta.address_id
    left join aux.assessor_summary ass using(address)
    where ass.residential
);

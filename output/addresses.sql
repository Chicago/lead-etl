DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

with test_addresses as (
    select distinct (address_id) address_id from aux.test_addresses
)

select a.id address_id, (ta.address_id is not null or ass.residential) as residential,
    a.census_tract_id, a.ward_id
    from aux.addresses a left join test_addresses ta on a.id = ta.address_id
    left join aux.assessor_summary ass using(address)
);

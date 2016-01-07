DROP TABLE IF EXISTS output.kid_addresses;

CREATE TABLE output.kid_addresses AS (

with kid_addresses as (
    select kid_id,address_id,
    min(sample_date) as min_test_date,
    max(sample_date) as max_test_date,
    bool_or(minmax) as minmax
    
    from aux.tests_geocoded
    group by kid_id, address_id
)

select ka.address_id, minmax, k.date_of_birth, ka.min_test_date, ka.max_test_date
from kid_addresses ka
join aux.kids k on ka.kid_id = k.id
where address_id is not null
);

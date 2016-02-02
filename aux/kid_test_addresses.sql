DROP TABLE IF EXISTS aux.kid_test_addresses;

CREATE TABLE aux.kid_test_addresses AS (

select kid_id, address_id, 
min(sample_date) AS min_date, 
max(sample_date) as max_date, 
count(*) AS num_tests

FROM output.tests

GROUP BY kid_id, address_id
);

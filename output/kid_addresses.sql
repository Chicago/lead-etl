DROP TABLE IF EXISTS output.kid_addresses_0101;


CREATE TABLE output.kid_addresses_0101 AS (

WITH

year_test_addresses AS (
SELECT kid_id, address_id, date_floor(min_date, 1, 1) date, min_date
FROM 
aux.kid_test_addresses
WHERE
extract(year from min_date) between 2000 and 2001 and
address_id is not null
),


year_first_test_date AS (
SELECT kid_id, date, min(min_date) as min_date
FROM year_test_addresses
group by 1,2
)

SELECT kid_id, date, address_id, 
-- is this the address for the next addressed test for this kid? (could be multiple if tests have same date)
t.min_date = t2.min_date as address_current_test, 
first_ebll_date, kid_ethnicity, date_of_birth

FROM year_test_addresses t
LEFT JOIN year_first_test_date t2 USING (kid_id, date)
JOIN aux.kids k on k.id = kid_id
JOIN aux.kid_ethnicity USING (kid_id)

);

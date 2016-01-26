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

SELECT kid_id, date, address_id, t.min_date = t2.min_date as first

FROM year_test_addresses t
LEFT JOIN year_first_test_date t2 USING (kid_id, date);

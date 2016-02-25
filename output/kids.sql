DROP TABLE IF EXISTS output.kids;

CREATE TABLE output.kids AS (

WITH 

first_bll6 AS ( select * FROM output.tests t where first_bll6 and 1=1),
first_bll10 AS ( select * FROM output.tests where first_bll10 and 1=1),
first AS ( select * FROM output.tests where first and 1=1),

wic AS ( 
    select kid_id, min(date) wic_date 
    from aux.kid_wic_addresses
    where 1=1 
    group by 1
),

summary AS ( select kid_id,
    count(distinct address_id) address_count, count(*) test_count,
    avg(bll) as mean_bll, max(bll) as max_bll,
    max(date) as last_sample_date
    from output.tests
    where 1=1
    group by kid_id),

-- do this query so that the table is compatibe with revise
kids as (
    select * from wic 
    full outer join summary using (kid_id) 
    left join aux.kids using (kid_id)
)

SELECT k.*,
    first_bll6.date first_bll6_sample_date,
    first_bll10.date first_bll10_sample_date,
    first.date as first_sample_date,
    first.address_id as first_sample_address_id,
    first_bll6.address_id as first_bll6_address_id

FROM kids k
LEFT JOIN first_bll6 USING (kid_id)
LEFT JOIN first_bll10 USING (kid_id)
LEFT JOIN first USING (kid_id)
where date_of_birth is not null
);

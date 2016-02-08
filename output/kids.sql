DROP TABLE IF EXISTS output.kids;

CREATE TABLE output.kids AS (

WITH 

first_bll6 AS ( select * FROM output.tests t where first_bll6),
first_bll10 AS ( select * FROM output.tests where first_bll10),
max AS ( select * FROM output.tests where max),
first AS ( select * FROM output.tests where first),
last AS ( select * FROM output.tests where last),

wic AS ( select kid_id, min(date) min_date 
from aux.kid_wic_addresses group by 1),

summary AS ( select kid_id,
    count(distinct address_id) address_count, count(*) test_count,
    avg(bll) as mean_bll
    from output.tests group by kid_id)

SELECT k.*, address_count, test_count,
    first_bll6.sample_date first_bll6_sample_date,
    first_bll10.sample_date first_bll10_sample_date,
    max.bll max_bll,
    mean_bll,
    first.sample_date as first_sample_date,
    last.sample_date as last_sample_date,
    wic.min_date AS wic_date

FROM aux.kids k
LEFT JOIN summary using (kid_id)
LEFT JOIN wic using (kid_id)
LEFT JOIN first_bll6 USING (kid_id)
LEFT JOIN first_bll10 USING (kid_id)
LEFT JOIN max USING (kid_id)
LEFT JOIN first USING (kid_id)
LEFT JOIN last USING (kid_id)
where date_of_birth is not null
);

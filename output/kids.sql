DROP TABLE IF EXISTS output.kids;

CREATE TABLE output.kids AS (

WITH 

first_bll6 AS ( select * FROM output.tests t where first_bll6),
first_bll10 AS ( select * FROM output.tests where first_bll10),
max AS ( select * FROM output.tests where max),
first AS ( select * FROM output.tests where first),
last AS ( select * FROM output.tests where last),

wic AS ( select distinct kid_id from aux.kid_wics ),

counts AS ( select kid_id,
    count(distinct address_id) address_count, count(*) test_count 
    from output.tests group by kid_id)

SELECT k.*, address_count, test_count,
    first_bll6.sample_date first_bll6_sample_date,
    first_bll10.sample_date first_bll10_sample_date,
    max.bll max_bll,
    first.sample_date as first_sample_date,
    last.sample_date as last_sample_date,
    wic.kid_id is not null AS wic

FROM aux.kids k
JOIN counts using (kid_id)
LEFT JOIN wic using (kid_id)
LEFT JOIN first_bll6 USING (kid_id)
LEFT JOIN first_bll10 USING (kid_id)
LEFT JOIN max USING (kid_id)
LEFT JOIN first USING (kid_id)
LEFT JOIN last USING (kid_id)

);

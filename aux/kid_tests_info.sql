drop table if exists aux.kid_tests_info;

create table aux.kid_tests_info as (

WITH tests AS (
    select *,
        row_number() OVER
        (PARTITION BY kid_id ORDER BY sample_date ASC) as test_number
    from aux.tests join aux.kid_tests using (test_id) join aux.kids using (kid_id)
    WHERE kids.date_of_birth is not null AND sample_date >= kids.date_of_birth
),

-- minmax is the first test to produce the maximum bll state (bll > 5 or bll <= 5)
first_bll6 AS (
    select distinct on(kid_id) kid_id,test_id
    from tests
    where bll > 5
    order by kid_id, sample_date asc, test_id asc
),

first_bll10 AS (
    select distinct on(kid_id) kid_id,test_id
    from tests
    where bll > 9
    order by kid_id, sample_date asc, test_id asc
)

select tests.kid_id, test_id, 
    first_bll6.test_id is not null as first_bll6,
    first_bll10.test_id is not null as first_bll10,
    test_number = 1 as first
from tests 
left join first_bll6 using (test_id)
left join first_bll10 using (test_id)
);


ALTER TABLE aux.kid_tests_info ADD PRIMARY KEY (test_id);

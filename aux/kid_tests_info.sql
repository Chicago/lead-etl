drop table if exists aux.kid_tests_info;

create table aux.kid_tests_info as (

WITH kid_tests1 AS (
	select kid_id, test_id,
		row_number() OVER (PARTITION BY kid_id ORDER BY sample_date ASC) as test_number
	from aux.tests t
	join aux.kid_tests kt on t.id = kt.test_id
), 

-- minmax is the first test to produce the maximum bll state (bll > 5 or bll <= 5)
first_ebll AS (
	select distinct on(kid_id) kid_id,test_id
	from aux.tests m join kid_tests1 kt on m.id = kt.test_id 
	order by kid_id, bll > 5 desc, sample_date asc, m.id asc
),

max_bll AS (
	select distinct on(kid_id) kid_id, test_id
	from aux.tests m join kid_tests1 kt on m.id = kt.test_id 
	order by kid_id, bll desc, sample_date asc, m.id asc
),

last AS (
	select distinct on(kid_id) kid_id,test_id
    from kid_tests1
	order by kid_id, test_number desc 
)

select kid_tests1.*, 
	first_ebll.test_id is not null as first_ebll,
	max_bll.test_id is not null as max_bll,
	kid_tests1.test_number = 1 as first,
    last.test_id is not null as last
from kid_tests1 
left join first_ebll using (test_id)
left join max_bll using (test_id)
left join last using (test_id)
);


ALTER TABLE aux.kid_tests_info ADD PRIMARY KEY (test_id);

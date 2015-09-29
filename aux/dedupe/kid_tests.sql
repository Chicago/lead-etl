drop table if exists aux.kid_tests;

create table aux.kid_tests as (

with kid_tests0 AS (
	select k.id kid_id, m.id test_id, m.sample_date, 
            m.sex, m.bll, ta.address_id, m.apt, m.sample_type
	from aux.kids_initial k join aux.tests m using (first_name, last_name, date_of_birth)
            left join aux.test_addresses ta on m.id = ta.test_id
), 

-- deduplicate tests. do it here because we want to get test_numbers right but we also want to use the deduplicated names and dates of birth
kid_tests_distinct AS (
    select kid_id, min(test_id) as test_id, sample_date
    from kid_tests0 group by kid_id, sample_date, sex, bll, address_id, apt, sample_type
),

kid_tests1 AS (
	select kt.test_id, kc.id1 as kid_id, kc.id2 as kid_initial_id,
		row_number() OVER (PARTITION BY kc.id1 ORDER BY kt.sample_date ASC, kt.test_id asc) as test_number
	from kid_tests_distinct kt
	join aux.kid_components kc on kt.kid_id = kc.id2
), 

-- minmax is the first test to produce the maximum bll state (bll > 5 or bll <= 5)
minmax AS (
	select distinct on(kid_id) kid_id,test_id
	from aux.tests m join kid_tests1 kt on m.id = kt.test_id 
	order by kid_id, bll > 5 desc, sample_date asc, m.id asc
),

max AS (
	select distinct on(kid_id) kid_id,test_id
	from aux.tests m join kid_tests1 kt on m.id = kt.test_id 
	order by kid_id, bll desc, sample_date asc, m.id asc
)

select kid_tests1.*, 
	minmax.test_id is not null as minmax,
	max.test_id is not null as max,
	kid_tests1.test_number = 1 as min
from kid_tests1 
left join minmax using (test_id)
left join max using (test_id)
);


ALTER TABLE aux.kid_tests ADD PRIMARY KEY (test_id);

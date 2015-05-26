drop table if exists aux.kid_tests;

create table aux.kid_tests as (

with kid_tests0 AS (
	select k.id kid_id, m.id test_id, m.sample_date
	from aux.kids_initial k join aux.tests m on
		m.first_name = k.first_name and
		m.last_name = k.last_name and
		m.date_of_birth = k.date_of_birth
), 

kid_tests1 AS (
	select kt.test_id, kc.id1 as kid_id, kc.id2 as kid_initial_id,
		row_number() OVER (PARTITION BY kc.id1 ORDER BY kt.sample_date ASC, kt.test_id asc) as test_number
	from kid_tests0 kt
	join aux.kid_components kc on kt.kid_id = kc.id2
), 

-- minmax is the first test to produce the maximum bll state (bll > 5 or bll <= 5)
minmax AS (
	select distinct on(kid_id) kid_id,test_id
	from aux.tests m join kid_tests1 kt on m.id = kt.test_id 
	order by kid_id, bll > 5 desc, sample_date asc, m.id asc
)

select kid_tests1.*, 
	minmax.test_id is not null as minmax,
	kid_tests1.test_number = 1 as min
from kid_tests1 
left join minmax using (test_id)
);


ALTER TABLE aux.kid_tests ADD PRIMARY KEY (test_id);

drop table if exists aux.address_tests;

create table aux.address_tests as (

select t.id test_id,
	count(*) count,
	sum(t2.minmax::int) as kid_count,
		
	sum((t2.bll > 5)::int) as ebll_test_count,
	sum((t2.bll > 5)::int)::decimal/count(*) ebll_test_ratio,
	avg(CASE WHEN t2.bll > 5 THEN t2.bll ELSE null END) avg_ebll,
		
	sum((t2.bll > 5 and t2.minmax)::int) as ebll_kid_count,
	CASE WHEN sum((t2.minmax)::int) > 0 THEN sum((t2.bll > 5 and t2.minmax)::int)::decimal/sum((t2.minmax)::int) ELSE 0 END as ebll_kid_ratio
from aux.tests_geocoded t
left join aux.tests_geocoded t2 on
	t2.address_id = t.address_id and
	t2.sample_date < t.sample_date
group by t.id

);

alter table aux.address_tests add primary key(test_id);

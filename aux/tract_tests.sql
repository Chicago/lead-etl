drop table if exists aux.tract_tests;

create table aux.tract_tests as (
	select census_tract_id, 
		date_part('year', sample_date) as year,
		
		count(*) as test_count,
		sum(minmax::int) as kid_count,
		
		sum((bll > 5)::int) as ebll_test_count,
		sum((bll > 5)::int)::decimal/count(*) ebll_test_ratio,
		avg(CASE WHEN bll > 5 THEN bll ELSE null END) avg_ebll,
		
		sum((bll > 5 and minmax)::int) as ebll_kid_count,
		CASE WHEN sum((minmax)::int) > 0 THEN sum((bll > 5 and minmax)::int)::decimal/sum((minmax)::int) ELSE 0 END as ebll_kid_ratio
	from aux.tests_geocoded 
	group by census_tract_id, date_part('year', sample_date)
);

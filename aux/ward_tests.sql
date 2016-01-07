drop table if exists aux.ward_tests;

create table aux.ward_tests as (
	select ward_id, 
		date_part('year', sample_date) as year,
		1 as years,
		count(*) as test_count,
		sum(minmax::int) as kid_count,
		
		sum((bll > 5)::int) as ebll_test_count,
		sum((bll > 5)::int)::decimal/count(*) ebll_test_ratio,
		avg(CASE WHEN bll > 5 THEN bll ELSE null END) avg_ebll,
		
		sum((bll > 5 and minmax)::int) as ebll_kid_count,
		CASE WHEN sum((minmax)::int) > 0 THEN sum((bll > 5 and minmax)::int)::decimal/sum((minmax)::int) ELSE 0 END as ebll_kid_ratio
	from aux.tests_geocoded 
	group by ward_id, date_part('year', sample_date)
);

insert into aux.ward_tests (
	select ward_id, y as year, 
		-1 as years,
		sum(test_count) as test_count,
		sum(kid_count) as kid_count,
		
		sum(ebll_test_count) as ebll_test_count,
		sum(ebll_test_count)::decimal/sum(test_count) ebll_test_ratio,
		sum(avg_ebll*ebll_test_count)::decimal/sum(ebll_test_count) avg_ebll,
		
		sum(ebll_kid_count) as ebll_kid_count,
		CASE WHEN sum(kid_count) > 0 THEN sum(ebll_kid_count)::decimal/sum(kid_count) ELSE 0 END as ebll_kid_ratio
	from generate_series(1990, 2013) y
	join aux.ward_tests t on year <= y
	group by ward_id, y
);

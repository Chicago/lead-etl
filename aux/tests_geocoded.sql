drop table if exists aux.tests_geocoded;

create table aux.tests_geocoded as (
	select b.kid_id, t.id, t.sex, t.bll, b.minmax, b.min, b.maxmax, b.test_number,
	b.kid_initial_id, t.sample_date, t.sample_type,
	g.address_id, g.method address_method,
	a.address, a.geom,a.census_tract_id, a.ward_id, a.community_area_id
	from aux.kid_tests b
	join aux.kids k on b.kid_id = k.id
	join aux.tests t on b.test_id = t.id 
	left join aux.test_addresses g on t.id = g.test_id  
	left join aux.addresses a on g.address_id = a.id
);

-- create index tests_geocoded_census_sample_idx on aux.tests_geocoded (census_tract_id, sample_date);

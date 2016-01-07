drop table if exists output.tract_year;

create table output.tract_year as (
select
		c.geoid10 census_tract_id,
		y as year,

		ab.test_count,
		ab.kid_count test_kid_count,
		ab.ebll_kid_count ebll_kid_count,
		ab.ebll_kid_ratio ebll_kid_ratio,
		ab.ebll_test_count ebll_test_count,
		ab.ebll_test_ratio ebll_test_ratio,
		ab.avg_ebll avg_ebll,
		
		h.count inspection_count,
		h.hazard_int_count,
		h.hazard_ext_count,
		h.hazard_int_ratio,
		h.hazard_ext_ratio,
		h.compliance_count,
		h.compliance_ratio,
		h.avg_init_to_comply_days,
		h.pct_inspected
from input.census_tracts c
cross join generate_series(1990,2013) y
left join aux.tract_tests ab
	on c.geoid10 = ab.census_tract_id
	and y = ab.year
left join aux.tract_inspections h
	on c.geoid10 = h.census_tract_id
	and y = h.year
);
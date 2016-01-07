drop table if exists output.ward_year;

create table output.ward_year as (
select
		w.ward_id ward_id,
		y as year,
		ys as years,
		
		ab.test_count,
		ab.kid_count test_kid_count,
		ab.ebll_kid_count,
		ab.ebll_kid_ratio,
		ab.ebll_test_count,
		ab.ebll_test_ratio,
		ab.avg_ebll,
		
		h.count inspection_count,
		h.hazard_int_count,
		h.hazard_ext_count,
		h.hazard_int_ratio,
		h.hazard_ext_ratio
from aux.wards w
cross join generate_series(1990,2013) y
cross join unnest('{1,-1}'::int[]) ys
left join aux.ward_tests ab
	on w.ward_id = ab.ward_id
	and y = ab.year
	and ys = ab.years
left join aux.ward_inspections h
	on w.ward_id = h.ward_id
	and y = h.year
	and ys = h.years
);
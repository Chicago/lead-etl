drop table if exists aux.kid_ethnicity;

create table aux.kid_ethnicity as (
with ethnicity as (
select 
	k.id kid_id,
	s.surname is null surname_null,
	s.ethnicity surname_ethnicity,
	coalesce(race_pct_white*s.pct_white/100, race_pct_white, s.pct_white) p_white,
    coalesce(race_pct_black*pct_black/100, race_pct_black, s.pct_black)  p_black,
    coalesce(race_pct_asian*pct_api/100, race_pct_asian, pct_api) p_asian,
    coalesce(race_pct_latino*pct_hispanic/100, race_pct_latino, pct_hispanic) p_hispanic
from aux.kids k
left join input.surnames s on k.last_name = s.surname
left join aux.tests_geocoded t on k.id = t.kid_id
left join aux.acs on t.census_tract_id = acs.geo_id2
where t.minmax
)
select e.*,
CASE 
	WHEN e.p_white > greatest(e.p_black, e.p_hispanic, e.p_asian, 0) THEN 'white'
	WHEN e.p_black > greatest(e.p_hispanic, e.p_asian, 0) THEN 'black'
	WHEN e.p_hispanic > greatest(e.p_asian,0) THEN 'hispanic'
	WHEN e.p_asian > 0 THEN 'asian'
	ELSE null
END as kid_ethnicity

from ethnicity e
);
drop table if exists aux.kid_ethnicity;

create table aux.kid_ethnicity as (
with ethnicity as (
select 
	k.id kid_id,
	k.last_name,
	s.surname is null surname_null,
	s.ethnicity surname_ethnicity,
	coalesce(acs.race_pct_white*s.pct_white/100, acs.race_pct_white, s.pct_white/100) p_white,
    coalesce(acs.race_pct_black*s.pct_black/100, acs.race_pct_black, s.pct_black/100)  p_black,
    coalesce(acs.race_pct_asian*s.pct_api/100, acs.race_pct_asian, s.pct_api/100) p_asian,
    coalesce(acs.race_pct_hispanic*s.pct_hispanic/100, acs.race_pct_hispanic, s.pct_hispanic/100) p_hispanic
from aux.kids k
left join input.surnames s on k.last_name = s.surname
left join aux.tests_geocoded t on k.id = t.kid_id
left join output.acs on 
    acs.census_tract_id = t.census_tract_id and
    acs.year = least ( 2013, greatest( date_part('year', k.date_of_birth), 2009 ))
where t.test_number = 1
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
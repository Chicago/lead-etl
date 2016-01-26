drop table if exists aux.kid_ethnicity;

-- calculate probability of ethnicity (E) given surname (S) and census tract and year (T)
-- know P(E|S) from census surname data, know P(E|T) from american commnuity survey
-- assuming surname and tract and independent conditioned on ethnicity
-- i.e. P(E,S,T) = P(S|E)P(T|E)*P(E)
-- then P(E|S,T) is proportional to P(E|S)P(E|T)*P(E)
-- where P(E) is just the national ethnicity distribution which we've hardcoded

create table aux.kid_ethnicity as (
with ethnicity as (
select distinct on (k.id)
	k.id kid_id,
	k.last_name,
	s.surname is null surname_null,
	s.ethnicity surname_ethnicity,
	coalesce(acs.race_pct_white*s.pct_white/100, acs.race_pct_white, s.pct_white/100)/.774 p_white,
    coalesce(acs.race_pct_black*s.pct_black/100, acs.race_pct_black, s.pct_black/100)/.132  p_black,
    coalesce(acs.race_pct_asian*s.pct_api/100, acs.race_pct_asian, s.pct_api/100)/.054 p_asian,
    coalesce(acs.race_pct_hispanic*s.pct_hispanic/100, acs.race_pct_hispanic, s.pct_hispanic/100)/.174 p_hispanic
from aux.kids k
left join input.surnames s on k.last_name = s.surname
left join aux.kid_test_addresses t on k.id = t.kid_id
left join aux.addresses a on a.id = address_id
left join output.acs on 
    acs.census_tract_id = cast(a.census_tract_id as double precision) and
    acs.year = least ( 2013, greatest( date_part('year', k.date_of_birth), 2009 ))
order by k.id, min_date asc
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

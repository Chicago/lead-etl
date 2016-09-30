drop table if exists output.kid_ethnicity;

-- calculate probability of ethnicity (E) given surname (S) and census tract and year (T)
-- know P(E|S) from census surname data, know P(E|T) from american commnuity survey
-- assuming surname and tract and independent conditioned on ethnicity
-- i.e. P(E,S,T) = P(S|E)P(T|E)*P(E)
-- then P(E|S,T) is proportional to P(E|S)P(E|T)/P(E)
-- where P(E) is just the national ethnicity distribution which we've hardcoded

-- TODO: use age-specific ethnicity stats from ACS
create table output.kid_ethnicity as (
with ethnicity as (
select distinct on (kid_id)
	kid_id,
	last_name,
	s.surname is null surname_null,
	s.ethnicity surname_ethnicity,
	coalesce(acs.race_prop_white*s.pct_white/100, acs.race_prop_white, s.pct_white/100)/.774 p_white,
    coalesce(acs.race_prop_black*s.pct_black/100, acs.race_prop_black, s.pct_black/100)/.132  p_black,
    coalesce(acs.race_prop_asian*s.pct_api/100, acs.race_prop_asian, s.pct_api/100)/.054 p_asian,
    coalesce(acs.race_prop_hispanic*s.pct_hispanic/100, acs.race_prop_hispanic, s.pct_hispanic/100)/.174 p_hispanic
from aux.kids k
left join input.surnames s on k.last_name = s.surname
left join output.kid_addresses using (kid_id)
left join aux.addresses a using (address_id)
left join output.acs on 
    acs.census_tract_id = a.census_tract_id::decimal and
    -- get appropriate year between 2009 and 2014
    acs.year = least (2014, 
        greatest(extract(year from k.date_of_birth), 2009))
order by kid_id, address_min_date asc
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

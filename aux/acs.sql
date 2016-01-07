DROP TABLE IF EXISTS aux.acs;

CREATE TABLE aux.acs AS (
	select
		geo_id2,
		-- race
		dp05.HC03_VC78 race_pct_white,
		dp05.HC03_VC81 race_pct_asian,
		dp05.HC03_VC79 race_pct_black,
		dp05.HC03_VC83 race_pct_other,
		dp05.HC03_VC88 race_pct_latino,
		
		dp05.HC01_VC77 race_count_total,
		dp05.HC01_VC78 race_count_white,
		dp05.HC01_VC81 race_count_asian,
		dp05.HC01_VC79 race_count_black,
		dp05.HC01_VC83 race_count_other,
		dp05.HC01_VC88 race_count_latino,

		CASE
			WHEN dp05.HC03_VC78 > greatest(dp05.HC03_VC81, dp05.HC03_VC79, dp05.HC03_VC83, dp05.HC03_VC88, 0) THEN 'white'
			WHEN dp05.HC03_VC81 > greatest(dp05.HC03_VC79, dp05.HC03_VC83, dp05.HC03_VC88, 0) THEN 'asian'
			WHEN dp05.HC03_VC79 > greatest(dp05.HC03_VC83, dp05.HC03_VC88, 0) THEN 'black'
			WHEN dp05.HC03_VC83 > greatest(dp05.HC03_VC88, 0) THEN 'other'
			WHEN dp05.HC03_VC88 > 0 THEN 'latino'
			ELSE null
		END as ethnicity,
		-- education
		dp02.HC03_VC86 edu_pct_9th,
		dp02.HC03_VC87 edu_pct_12th,
		dp02.HC03_VC88 edu_pct_high_school,
		dp02.HC03_VC89 edu_pct_some_college,
		dp02.HC03_VC90 + dp02.HC03_VC91 edu_pct_college,
		dp02.HC03_VC92 edu_pct_advanced,
		
		dp02.HC01_VC85 edu_count_total,
		dp02.HC01_VC86 edu_count_9th,
		dp02.HC01_VC87 edu_count_12th,
		dp02.HC01_VC88 edu_count_high_school,
		dp02.HC01_VC89 edu_count_some_college,
		dp02.HC01_VC90 + dp02.HC01_VC91 edu_count_college,
		dp02.HC01_VC92 edu_count_advanced,
		
		-- econ
		dp02.HC01_VC04 families_count_total,
		dp02.HC01_VC04*dp03.HC03_VC161/100 families_count_poverty,
		dp03.HC03_VC161 families_pct_poverty,
		
		-- health insurance
		dp03.HC01_VC130 health_count,
		dp03.HC01_VC131 health_count_insured,
		dp03.HC01_VC132 health_count_insured_private,
		dp03.HC01_VC133 health_count_insured_public,
		dp03.HC01_VC134 health_count_uninsured,
		dp03.HC01_VC137 health_minors_count,
		dp03.HC01_VC138 health_minors_count_uninsured,
		
		dp04.HC01_VC03 housing_count,
		dp04.HC01_VC05 housing_count_vacant,
		dp04.HC01_VC63 housing_count_occupied,
		dp04.HC01_VC68 housing_count_owner,
		dp04.HC01_VC65 housing_count_renter
	from input.acs_13_5yr_dp02 dp02
	join input.acs_13_5yr_dp03 dp03 using (geo_id2)
	join input.acs_13_5yr_dp04 dp04 using (geo_id2)
	join input.acs_13_5yr_dp05 dp05 using (geo_id2)
);
DROP TABLE IF EXISTS aux.kids_initial;
CREATE TABLE aux.kids_initial AS (
	SELECT first_name, --(regexp_split_to_array(first_name, ' '))[1] first_name, 
	last_name, date_of_birth, count(*) as num_tests,
	first_name || last_name || date_of_birth::text as key,
	substring(first_name for 1) || substring(last_name for 1) as initials,
        array_agg(sample_date) as sample_dates,
        array_remove(array_agg(distinct sex order by sex), null) as sexes,
        array_agg(distinct clean_address) as addresses
	from aux.tests
	GROUP BY first_name, --(regexp_split_to_array(first_name, ' '))[1],
	last_name, date_of_birth
);

ALTER TABLE aux.kids_initial ADD COLUMN id serial;
ALTER TABLE aux.kids_initial ADD PRIMARY KEY (id);

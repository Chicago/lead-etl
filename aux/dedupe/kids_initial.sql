DROP TABLE IF EXISTS aux.kids_initial;
CREATE TABLE aux.kids_initial AS (
	SELECT first_name, --(regexp_split_to_array(first_name, ' '))[1] first_name, 
	last_name, date_of_birth, count(*) as num_tests,
	first_name || last_name || date_of_birth::text as key,
	substring(first_name for 1) || substring(last_name for 1) as initials,
	min(sample_date) as min_sample_date,
	max(sample_date) as max_sample_date
	from aux.tests
	GROUP BY first_name, --(regexp_split_to_array(first_name, ' '))[1],
	last_name, date_of_birth
);

ALTER TABLE aux.kids_initial ADD COLUMN id serial;
ALTER TABLE aux.kids_initial ADD PRIMARY KEY (id);
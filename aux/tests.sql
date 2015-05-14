DROP TABLE IF EXISTS aux.tests CASCADE;

-- drop when essential field (sample_date, bll, date_of_birth, first_name, last_name) is null
-- clean names
-- use geometry instead of xcoord, ycoord
-- clean sex
-- remove apartment from address

CREATE TABLE aux.tests AS (
    WITH tests AS (
        select first_name, mi, last_name, date_of_birth, sex, bll, sample_type, sample_date, lab_id, address, 
        	clean_address, apt, city, true as currbllshort
        from input.currbllshort
        UNION ALL
        select first_name, null as mi, last_name, date_of_birth, sex, bll, sample_type, sample_date, lab as lab_id, address, 
        	cleaned_address as clean_address, apt, city, false as currbllshort
        from input.tests
        where sample_date < '2004-01-01'
    )

	SELECT regexp_replace(first_name, '\W', '', 'g') first_name, mi, regexp_replace(last_name, '\W', '', 'g') last_name, 
		date_of_birth,
		CASE WHEN sex IN ('M','F') THEN sex ELSE null END as sex,
		bll, sample_type,sample_date,
		lab_id, 
		CASE WHEN address NOT IN ('NA','N/A', 'SEE NOTE') THEN address ELSE null END as address, 
		clean_address, apt, city,
		regexp_replace(
			regexp_replace(coalesce(clean_address,address), '[^\w \*]','','g'),
			'(([^ ]* ){3,}(AVE|BLVD|CT|DR|HWY|PKWY|PL|RD|ROW|SQ|ST|TER|WAY))( .*)$', '\1') as clean_address2,
		currbllshort
	FROM tests
	WHERE bll is not null and sample_date is not null and date_of_birth is not null and first_name is not null and last_name is not null
);

ALTER TABLE aux.tests2 ADD COLUMN id serial PRIMARY KEY;
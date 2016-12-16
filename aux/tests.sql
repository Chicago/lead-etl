DROP TABLE IF EXISTS aux.tests CASCADE;

-- drop when essential field (sample_date, bll, date_of_birth, first_name, last_name) is null
-- clean names
-- use geometry instead of xcoord, ycoord
-- clean sex
-- remove apartment from address
-- unique tests only (via UNION)

CREATE TABLE aux.tests AS (
    WITH tests AS (
        select first_name, mi, last_name, date_of_birth, sex, 
            bll, sample_type, sample_date, analysis_date, reported_date,
            lab_id, address, clean_address, apt, city,
            geocode_house_low, geocode_pre, geocode_street_name, 
            clean_street_type as geocode_street_type,
            true as currbllshort
        from input.currbllshort
        UNION
        -- get rid of whitespace and set to null before casting
        select first_name, null as mi, last_name,
            nullif(regexp_replace(date_of_birth, '\s', '', 'g'), '')::date, 
            sex, nullif(regexp_replace(bll, '\s', '', 'g'), '')::int, sample_type, 
            nullif(regexp_replace(sample_date, '\s', '', 'g'), '')::date, null, null,
            lab as lab_id, 
            address, cleaned_address, apt, city,
            geocode_house_low, geocode_pre, geocode_street_name, geocode_street_type,
            false
        from input.m7
        WHERE nullif(regexp_replace(sample_date, '\s', '', 'g'), '')::date < '2004-01-01'
    )

    SELECT  -- clean non-alpha characters characters
        regexp_replace(upper(first_name), '[^A-Z]', '', 'g') first_name, mi,
        regexp_replace(upper(last_name), '[^A-Z]', '', 'g') last_name, 
        date_of_birth,
        -- null invalid sex
        CASE WHEN sex IN ('M','F') THEN sex ELSE null END as sex,
        bll,
        CASE
            WHEN lab_id = 'C16' THEN 'V'        -- lab C16 is misreported as capillary
            WHEN sample_type = 'F' THEN 'C'     -- F is for fingerstick, same as capillary
            ELSE sample_type
        END AS sample_type,
        sample_date, reported_date, analysis_date,
        lab_id,
        -- form geocode addresses from components
        CASE WHEN city ilike 'CH%' THEN
        geocode_house_low || ' ' || geocode_pre || ' ' || geocode_street_name || ' ' || geocode_street_type 
        ELSE null END as geocode_address,

        CASE WHEN city ilike 'CH%' THEN
            CASE WHEN address NOT IN ('NA','N/A', 'SEE NOTE') THEN address ELSE null END 
        ELSE null END as address, 
        CASE WHEN city ilike 'CH%' THEN
            CASE WHEN coalesce(clean_address, address) NOT IN ('NA','N/A', 'SEE NOTE')
                 THEN coalesce(clean_address, address) ELSE null END 
        ELSE null END as clean_address, 
        apt, city,
        currbllshort
    FROM tests
    -- only take tests with non-null first, last, dob, sample_date, bll
    WHERE bll is not null and 
        coalesce(sample_date, date_of_birth) is not null and 
        coalesce(first_name, last_name) is not null is not null 
);

ALTER TABLE aux.tests ADD COLUMN test_id serial PRIMARY KEY;

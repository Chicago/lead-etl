drop table if exists output.tests;

create table output.tests as (
select
        k.id kid_id,
        --k.first_name kid_first_name,
        --k.last_name kid_last_name,
        k.date_of_birth kid_date_of_birth,
        
        e.surname_null kid_surname_null,
        e.surname_ethnicity surname_ethnicity,
        e.kid_ethnicity kid_ethnicity,

        t.sex kid_sex,
        t.id test_id,
        t.sample_date test_date,
        date_part('year', t.sample_date) as year,
        t.sample_date - k.date_of_birth test_kid_age_days,
        t.bll test_bll,
        
        t.minmax test_minmax,
        t.min test_min,
        t.test_number,
        t.sample_type,
        
        k.minmax_test_number,
        k.minmax_bll,
        k.min_sample_date,
        
        t.address_id,
        t.address_method

from aux.kids k
join aux.tests_geocoded t on k.id = t.kid_id
left join aux.kid_ethnicity e on k.id = e.kid_id
);

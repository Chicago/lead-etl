drop table if exists output.tests;

create table output.tests as (
select
        k.id kid_id,
--        k.first_name kid_first_name,
--        k.last_name kid_last_name,
        k.date_of_birth kid_date_of_birth,
        e.surname_null kid_surname_null,
        e.kid_ethnicity kid_ethnicity,
        t.sex kid_sex,

        k.minmax_bll kid_minmax_bll,
        k.minmax_date kid_minmax_date,

        t.id test_id,
        t.sample_date test_date,
        t.sample_date - k.date_of_birth as test_kid_age_days,
        t.bll test_bll,
        t.minmax test_minmax,
        t.sample_type test_type,
        
        t.address_id,
        t.address_method

from aux.kids k
join aux.tests_geocoded t on k.id = t.kid_id
left join aux.kid_ethnicity e on k.id = e.kid_id
);

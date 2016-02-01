drop table if exists output.tests;

create table output.tests as (
    select test_id, kid_id, 
        CASE WHEN a.address in 
            ('5001 S MICHIGAN AVE', '1634 W POLK ST', '810 W MONTROSE AVE') 
        THEN null ELSE a.address_id END AS address_id,
        bll, sample_date,
        first, last, first_bll6, first_bll10, max
    
    from aux.tests t
    join aux.kid_tests_info kt using (test_id)
    left join aux.test_addresses ta using (test_id)
    left join aux.addresses a using (address_id)
    left join aux.kids k using (kid_id)
);

--create table output.tests as (
--select
--        k.id kid_id,
--        k.first_name kid_first_name,
--        k.last_name kid_last_name,
--        k.date_of_birth kid_date_of_birth,
--        e.surname_null kid_surname_null,
--        e.kid_ethnicity kid_ethnicity,
--        t.sex kid_sex,
--
--        k.minmax_bll kid_minmax_bll,
--        k.minmax_date kid_minmax_date,
--        k.max_bll kid_max_bll,
--        k.max_date kid_max_date,
--        k.max_sample_date kid_max_sample_date,
--        k.min_sample_date kid_min_sample_date,
--        t.test_number kid_test_number,
--
--        t.id test_id,
--        t.sample_date test_date,
--        t.sample_date - k.date_of_birth as test_kid_age_days,
--        t.bll test_bll,
--        t.minmax test_minmax,
--        t.sample_type test_type,
--        
--        --t.address_id,
--        CASE WHEN t.address in ('5001 S MICHIGAN AVE', '1634 W POLK ST', '810 W MONTROSE AVE') THEN null ELSE t.address_id END,
--        t.apt address_apt,
--
--        w.kid_id is not null as wic,
--        w.address_id::int as wic_address_id
--
--from aux.kids k
--join aux.tests_geocoded t on k.id = t.kid_id
--left join aux.kid_ethnicity e on k.id = e.kid_id
--left join aux.wic_kids w on t.kid_id = w.kid_id
--);
--
--with fill as (
--    select distinct on(t1.test_id) t1.test_id, t2.address_id
--    from output.tests t1 join output.tests t2 using (kid_id)
--    where t1.address_id is null and
--          t2.address_id is not null and
--          t1.test_date >= t2.test_date
--    order by t1.test_id, t2.test_date asc
--)
--UPDATE output.tests t set address_id = f.address_id
--FROM fill f
--where t.test_id = f.test_id;

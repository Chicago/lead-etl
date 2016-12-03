drop table if exists discontinuity.tests;

create table discontinuity.tests as (
    select k.kid_id,
        count(*) as tests_count,
        avg(bll) as tests_bll_average,
        max(bll) as tests_bll_max,
        min(bll) as tests_bll_min,
        count(distinct t.kid_id) as tests_kid_count,
        count(distinct CASE WHEN bll >= 6 THEN t.kid_id END) as tests_kid_bll6_count,
        count(distinct CASE WHEN bll >= 10 THEN t.kid_id END) as tests_kid_bll10_count,

        CASE WHEN count(distinct t.kid_id) > 0 THEN 
            count(distinct CASE WHEN bll >= 6 THEN t.kid_id END)*1.0/count(distinct t.kid_id) 
        END as tests_kid_bll6_prop,
        CASE WHEN count(distinct t.kid_id) > 0 THEN 
            count(distinct CASE WHEN bll >= 10 THEN t.kid_id END)*1.0/count(distinct t.kid_id)
        END as tests_kid_bll10_prop
    from discontinuity.max_bll_under1 k
    join output.kids using (kid_id)
    join discontinuity.addresses a using (kid_id)
    left join output.tests t
        on t.address_id = a.address_id and date < first_sample_date
    where first_sample_address
    group by 1
);

alter table discontinuity.tests add primary key (kid_id);

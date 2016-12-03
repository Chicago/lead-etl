drop table if exists discontinuity.investigations;

create table discontinuity.investigations as (
    select kid_id,
        count(referral_date) as investigations_referral_count,
        count(init_date) as investigations_init_count,
        count(comply_date) as investigations_comply_count,

        CASE WHEN count(init_date) > 0 THEN count(init_date)/count(referral_date) END as investigations_init_prop,
        CASE WHEN count(init_date) > 0 THEN count(comply_date)/count(referral_date) END as investigations_comply_prop,

        sum(hazard_ext::int) as investigations_hazard_ext_count,
        sum(hazard_int::int) as investigations_hazard_int_count,
        
        CASE WHEN count(hazard_ext) > 0 THEN avg(hazard_ext::int) END as investigations_hazard_ext_prop,
        CASE WHEN count(hazard_int) > 0 THEN avg(hazard_int::int) END as investigations_hazard_int_prop,

        min(first_sample_date - referral_date) as investigations_days_since_referral,
        min(first_sample_date - init_date) as investigations_days_since_init,
        min(first_sample_date - comply_date) as investigations_days_since_comply
    from 
    discontinuity.max_bll_under1 left join
    (select * from discontinuity.addresses 
    join output.kids using (kid_id)
    join output.investigations using (address_id)
    where coalesce(comply_date, init_date, referral_date) < first_sample_date and first_sample_address) t
    using (kid_id)
    group by 1
);

alter table discontinuity.investigations add primary key (kid_id);

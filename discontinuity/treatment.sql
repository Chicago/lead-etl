drop table if exists discontinuity.treatment;

create table discontinuity.treatment as (
    select kid_id,
        min(referral_date) as next_referral_date,
        min(init_date) as next_init_date,
        min(comply_date) as next_comply_date
    from discontinuity.max_bll_under1 
        join output.kids using (kid_id)
        join aux.kid_stellars using (kid_id)
        join stellar.ca_link on stellar_id = child_id
        join output.investigations using (addr_id)
    where referral_date >= first_sample_date
    group by 1
);

alter table discontinuity.treatment add primary key (kid_id);

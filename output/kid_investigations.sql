drop table if exists output.kid_investigations;

create table output.kid_investigations as (
    select kid_id,
        min(referral_date) as next_referral_date,
        min(init_date) as next_init_date,
        min(comply_date) as next_comply_date
    from output.kids
        join aux.kid_stellars using (kid_id)
        join stellar.ca_link on stellar_id = child_id
        join output.investigations using (addr_id)
    where referral_date >= first_sample_date
    group by 1
);

alter table output.kid_investigations add primary key (kid_id);

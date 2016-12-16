drop table if exists output.kid_investigations;

create table output.kid_investigations as (
    with kid_stellars as (
        select kid_id,
            first_sample_date, 
            stellar_id as child_id, 
            addr_id
        from output.kids
            join aux.kid_stellars using (kid_id)
            join stellar.ca_link on stellar_id = child_id
        group by 1,2,3,4
    ),
    investigations as (
        select kid_id,
            min(referral_date) as next_referral_date,
            min(init_date) as next_init_date,
            min(comply_date) as next_comply_date
        from kid_stellars
        join output.investigations using (addr_id)
        where referral_date >= first_sample_date
        group by 1
    ),
    events as (
        select kid_id, 
        min(CASE WHEN event_code in ('ENVPH', 'REINS') 
            THEN least(ref_date, due_date, comp_date) END
            ) as next_referral_date
        from kid_stellars
        join stellar.event on
            ((class = 'C' and id_number = child_id) or
             (class = 'I' and id_number = addr_id))
        where least(ref_date, due_date, comp_date) >= first_sample_date
        group by 1
    )
    select kid_id,
        least(i.next_referral_date, e.next_referral_date) 
            next_referral_date,
        next_init_date, next_comply_date
    from investigations i 
    full outer join events e using (kid_id)
);

alter table output.kid_investigations add primary key (kid_id);

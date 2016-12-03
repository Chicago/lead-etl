drop table if exists discontinuity.max_bll_under1;

create table discontinuity.max_bll_under1 as (
    select kid_id
    from output.kids_extra a 
    join output.kids_extra v using (kid_id)
    join output.kids using (kid_id)
    where 
    (not a.venal)
    and v.venal
    and a.max_bll_under1 is not null
    and v.max_bll_over1 is not null
    and first_sample_address_id is not null
    and first_sample_date between '1999-01-01' and '2012-09-01'
);

alter table discontinuity.max_bll_under1 add primary key (kid_id);

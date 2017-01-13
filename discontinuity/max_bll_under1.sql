drop table if exists discontinuity.max_bll_under1;

create table discontinuity.max_bll_under1 as (
    select kid_id
    from output.kids_extra a 
    join output.kids using (kid_id)
    where 
    (not a.venous)
    and a.max_bll_under1 is not null
    and first_sample_address_id is not null
);

alter table discontinuity.max_bll_under1 add primary key (kid_id);

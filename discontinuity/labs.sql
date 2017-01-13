drop table if exists discontinuity.labs;

create table discontinuity.labs as (
    select kid_id, lab_id
    from 
    discontinuity.max_bll_under1
    left join output.tests using (kid_id)
    where first
);

alter table discontinuity.labs add primary key (kid_id);

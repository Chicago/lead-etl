drop table if exists discontinuity.labs;

create table discontinuity.labs as (
    select kid_id, array_agg(lab_id)
    from 
    discontinuity.max_bll_under1 left join
    (select * from output.kids join output.tests using (kid_id)
        where date = first_sample_date
    ) t
    using (kid_id)
    group by 1
);

alter table discontinuity.labs add primary key (kid_id);

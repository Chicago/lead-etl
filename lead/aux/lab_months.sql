drop table if exists aux.lab_months;

create table aux.lab_months as (
with lab_months as (
    select test_lab.lab_id, 
        sample_type,
        date_trunc('month', sample_date) as month,
        count(*) as count,
        mode() WITHIN GROUP (ORDER BY bll ASC) as bll_mode,
        percentile_disc(ARRAY[.05,.10,.15,.20]) WITHIN GROUP (ORDER BY bll ASC) as bll_percentiles,
        percentile_disc(.05) WITHIN GROUP (ORDER BY bll ASC) as limit
    from aux.tests
    join aux.test_lab using (test_id)
    where test_lab.lab_id != 'ERR'
    group by 1,2,3
),

lods as (
    select l.lab_id, l.sample_type, l.month,
        sum((bll=bll_percentiles[1])::int) as limit_count
    from lab_months l 
    join aux.tests t on l.lab_id = t.lab_id and
        l.sample_type = t.sample_type and
        l.month = date_trunc('month', sample_date)
    group by 1,2,3
)

select *
from lab_months 
join lods using (lab_id, sample_type, month)
);

alter table aux.lab_months add primary key (lab_id, sample_type, month);

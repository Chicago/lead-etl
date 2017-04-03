drop table if exists aux.lab_months;

create table aux.lab_months as (

with tests as (
    select test_lab.lab_id, sample_type, bll, date_trunc('month', sample_date) as month
    From aux.tests
    join aux.test_lab using (test_id)
    where test_lab.lab_id != 'ERR'
),

lab_months as (
    select lab_id, sample_type, month,
        count(*) as count,
        mode() WITHIN GROUP (ORDER BY bll ASC) as bll_mode,
        percentile_disc(ARRAY[.05,.10,.15,.20]) WITHIN GROUP (ORDER BY bll ASC) as bll_percentiles,
        percentile_disc(.05) WITHIN GROUP (ORDER BY bll ASC) as limit
    from tests
    group by 1,2,3
),

lods as (
    select l.lab_id, l.sample_type, l.month,
        sum((bll=bll_percentiles[1])::int) as limit_count
    from lab_months l 
    join tests t using (lab_id, sample_type, month) 
    group by 1,2,3
)

select *
from lab_months 
join lods using (lab_id, sample_type, month)
);

alter table aux.lab_months add primary key (lab_id, sample_type, month);

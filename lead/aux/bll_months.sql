drop table if exists aux.bll_months;

create table aux.bll_months as (

-- these are the max limits found in lab_months
-- we only need to compute conditional means in a given month up to this value
with limits as (
    select month, max("limit") as max_limit
    from aux.lab_months
    group by 1
),

-- get tests labs with limit of 1 and count of at least 50
tests as (
    select month, bll
    from aux.tests t join aux.test_lab using (test_id)
    join aux.lab_months l on
        l.lab_id = test_lab.lab_id and
        t.sample_type = l.sample_type and
        date_trunc('month', t.sample_date) = l.month
    where "limit" = 1 and count >= 50
),

-- count number of blls under the above limits
sub_counts as (
    select month, bll, count(*) as count
    from tests join limits using (month)
    where bll <= max_limit
    group by 1,2
),

-- count total number of blls at those labs each month
counts as (
    select month, count(*) as total_count
    from tests
    group by 1
)

select month, bll, total_count,
    sum(count) over (partition by month order by bll) as count,
    -- weighted sum for mean
    (sum(count*bll) over w)/(sum(count) over w) as mean
from sub_counts join counts using (month)
window w as (partition by month order by bll)
);

alter table aux.bll_months add primary key (month, bll);

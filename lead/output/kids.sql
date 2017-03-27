DROP TABLE IF EXISTS output.kids;

CREATE TABLE output.kids AS (

WITH 

first_bll6 AS ( select * FROM output.tests t where first_bll6 and 1=1),
first_bll10 AS ( select * FROM output.tests where first_bll10 and 1=1),
first AS ( select * FROM output.tests where first and 1=1),

max_bll AS (
    select distinct on(kid_id) *
    from output.tests
    where 1=1
    order by kid_id, bll desc nulls last, date asc, test_id asc
),

max_bll0 AS (
    select distinct on(kid_id) *
    from output.tests
    where 1=1
    order by kid_id, bll0 desc, date asc, test_id asc
),

test_summary AS (
    select kid_id,
    count(distinct address_id) test_address_count, count(*) test_count,
    avg(bll) as mean_bll,
    min(date) as first_sample_date,
    max(date) as last_sample_date
    from output.tests
    where 1=1
    group by kid_id
),

blls AS (
    with bll_windows as (
        select kid_id, date, bll,
        coalesce(lag(date) OVER (PARTITION BY kid_id order by date asc), date_of_birth) as last_date,
        coalesce(lag(bll) OVER (PARTITION BY kid_id order by date asc), 0) as last_bll
        from output.tests join aux.kids using (kid_id)
        where (1=1)
    )

    select kid_id,
        avg(bll) as avg_bll,
        -- when last_sample_date = date_of_birth time series is a point
        -- make cumulative_bll null
        CASE WHEN min(last_date) != max(date) THEN
            sum((date - last_date)*(last_bll +(bll - last_bll)/2.0))
        END 
        as cumulative_bll,
        max(date) - min(last_date) as days
    from bll_windows
    group by 1
),
wic as (
    select kid_id, min(date) as first_wic_date
    from aux.kid_wic_min_date
    where (1=1)
    group by kid_id
),
kid_address_pre as (
    select kid_id, address_id, min(address_min_date) as date
    from output.kid_addresses
    group by kid_id, address_id
    UNION ALL
    select kid_id, address_id, max(address_max_date) as date
    from output.kid_addresses
    group by kid_id, address_id
),
kid_address_dates as (
    select kid_id, address_count,
        least(min_date, first_sample_date) as min_date,
        greatest(max_date, last_sample_date) as max_date
    from (
        select kid_id, count(distinct address_id) as address_count,
        min(date) as min_date, 
        max(date) as max_date
        from kid_address_pre
        where (1=1)
        group by 1
    ) t full outer join test_summary using (kid_id)
),
-- do this query so that the table is compatible with revise
-- to be in kids must either have an address entry 
-- coming from blood tests, wic, stellar
-- or a blood test
summary as (
    select * from kid_address_dates
    full outer join wic using (kid_id)
    full outer join test_summary using (kid_id)
    left join aux.kids using (kid_id)
)

SELECT s.*,
    max_bll.bll as max_bll,
    max_bll0.bll as max_bll0,
    blls.avg_bll,
    -- cumulative bll is measured in ug/dL * years
    blls.cumulative_bll / 365 as cumulative_bll,
    -- average cumulative bll is measured in ug/dL
    blls.cumulative_bll / blls.days as avg_cumulative_bll,

    first_bll6.date first_bll6_sample_date,
    first_bll10.date first_bll10_sample_date,
    max_bll.date as max_bll_sample_date,

    first.address_id as first_sample_address_id,
    first_bll6.address_id as first_bll6_address_id,
    first_bll10.address_id as first_bll10_address_id,
    max_bll.address_id as max_bll_address_id

FROM summary s
LEFT JOIN first_bll6 USING (kid_id)
LEFT JOIN first_bll10 USING (kid_id)
LEFT JOIN first USING (kid_id)
LEFT JOIN max_bll USING (kid_id)
LEFT JOIN max_bll0 USING (kid_id)
LEFT JOIN icare USING (kid_id)
LEFT JOIN blls USING (kid_id)
where date_of_birth is not null
);

alter table output.kids add primary key (kid_id);

drop table if exists output.kid_addresses;

create table output.kid_addresses as (
with wic_addresses as (
select kid_id, address_id, 
    min(date) as min_date, max(date) as max_date
from aux.kid_wic_addresses group by 1,2
),

test_addresses as (
select kid_id, address_id, 
    min(sample_date) as min_date, max(sample_date) as max_date
from output.tests group by 1,2
)

select kid_id, address_id, 
    w.min_date as wic_min_date, w.max_date as wic_max_date,
    t.min_date as test_min_date, t.max_date as test_max_date

from wic_addresses w 
FULL OUTER JOIN test_addresses t using (kid_id, address_id)

);

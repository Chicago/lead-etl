drop table if exists discontinuity.kids;

create temp table tests as (
    select k1.kid_id, ka.kid_id kid2_id,bll
    from discontinuity.max_bll_under1 
    join output.kids k1 using (kid_id)
    join discontinuity.addresses a using (kid_id)
    join output.kid_addresses ka using (address_id)
    join output.tests t on ka.kid_id = t.kid_id 
    where first_sample_address
        and ka.kid_id != k1.kid_id
        and ka.address_min_date < k1.first_sample_date
        and t.date < k1.first_sample_date
);

create index on tests (kid_id, kid2_id);

create table discontinuity.kids as (
with kids as (
    select kid_id, kid2_id,
        max(bll) kids_max_bll,
        avg(bll) kids_avg_bll,
        min(bll) kids_min_bll
    from tests
    group by 1,2
)

select kid_id, 
    count(distinct kid2_id) kids_past_kid_count,
    avg(kids_max_bll) kids_max_bll, 
    avg(kids_min_bll) kids_min_bll, 
    avg(kids_avg_bll) kids_avg_bll, 
    avg((kids_max_bll >= 6)::int) kids_bll6_prop,
    avg((kids_max_bll >= 10)::int) kids_bll10_prop
from discontinuity.max_bll_under1 left join kids using (kid_id)
group by 1
);

alter table discontinuity.kids add primary key (kid_id);

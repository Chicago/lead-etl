drop table if exists aux.labs_tests;

create table aux.labs_tests as (
with lab as (
    select *, child_id as stellar_id,
        samp_date as sample_date, pbb_rest as bll
        --,specm_id::int as sequential_id_sent_to_stellar 
    from stellar.lab
    --where specm_id ~ E'^\\d+$'
)

select ogc_fid, test_id
from aux.tests
join aux.kid_tests using (test_id)
join aux.kid_stellars using (kid_id)
join lab using (stellar_id, bll, sample_date)
group by 1,2
);

create index on aux.labs_tests (ogc_fid);
create index on aux.labs_tests (test_id);

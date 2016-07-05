drop table if exists output.labs;

create table output.labs as (
with lab_blls as (select lab_id, 
--        extract(year from sample_date) as year,
        bll, count(*) 
    from aux.tests group by 1,2),

lab_modes as (

select distinct on (lab_id--, year
    ) lab_id, --year, 
    bll as mode_bll from lab_blls order by lab_id, --year, 
    count desc),

lab_counts as (
    select lab_id, 
    --extract(year from sample_date) as year, 
    count(*) as test_count from aux.tests group by 1--,2
)

select * from lab_modes join lab_counts using (lab_id --, year
));

drop table if exists output.lab_years;

create table output.lab_years as (
with lab_blls as (select lab_id, 
        extract(year from sample_date) as year,
        sample_type,
        bll, count(*) 
    from aux.tests group by 1,2,3,4
),

lab_modes as (

select distinct on (lab_id, year, sample_type) 
    lab_id, year, sample_type,
    bll as mode_bll from lab_blls
    order by lab_id, year, sample_type, count desc
),

lab_counts as (
    select lab_id, 
    extract(year from sample_date) as year, 
    sample_type,
    count(*) as test_count from aux.tests
    group by 1,2,3
)

select * from lab_modes 
join lab_counts using (lab_id, year, sample_type));

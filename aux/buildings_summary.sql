drop table if exists aux.buildings_summary;

create table aux.buildings_summary as (

select distinct on ( f_add1 || ' ' || pre_dir1 || ' ' || st_name1 || ' ' || st_type1)
 f_add1 || ' ' || pre_dir1 || ' ' || st_name1 || ' ' || st_type1 address,
 bldg_condi,
 CASE WHEN year_built > 0 THEN year_built ELSE NULL END as year_built,
 CASE WHEN no_of_unit > 0 THEN no_of_unit ELSE NULL END as units,
 CASE WHEN stories > 0 THEN no_of_unit ELSE NULL END as stories,
 vacancy_st is not null as vacant
 from input.buildings
 order by  f_add1 || ' ' || pre_dir1 || ' ' || st_name1 || ' ' || st_type1, edit_date desc
 
 );
 
 alter table aux.buildings_summary add unique(address);
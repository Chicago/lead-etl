drop table if exists aux.assessor_summary;

create table aux.assessor_summary as (

select substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix as address,
        count(*) count,
        max(nullif("land_AV"::int,0)) land_value,
	max(nullif("Imp_Value"::int,0)) improved_value,
	max(nullif("total_Value"::int,0)) total_value,
	max(nullif(age::int,0)) age,
	max(no_apt::int) apartments,
	max(nullif(rooms::int, 0)) rooms,
	max(nullif(num_bed::int,0)) beds,
	max(nullif(num_full_baths::int,0) + num_half_baths::int) as baths,
	max(nullif(bldg_sq_ft::int, 0)) building_area,
	max(nullif(land_sq_ft::int,0)) land_area,
	array_agg(distinct type_res) type_res,
	array_agg(distinct use) use,
	bool_or(substring(imp_class for 1) in ('2','9')) as residential,
	array_agg(distinct imp_class) as classes,
	array_agg(distinct substring(imp_class for 1)) as class_types
from input.assessor
where city = 'CHICAGO'
group by substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix

);

alter table aux.assessor_summary add unique (address);

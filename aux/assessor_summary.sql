drop table if exists aux.assessor_summary;

create table aux.assessor_summary as (

select substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix as address,
	max((CASE WHEN bldg_sq_ft::int != '0' THEN bldg_sq_ft ELSE null END)::int) bldg_sq_ft,
	max((CASE WHEN land_sq_ft::int != '0' THEN land_sq_ft ELSE null END)::int) land_sq_ft,
	max((CASE WHEN "land_AV"::int != '0' THEN "land_AV" ELSE null END)::int) land_value,
	max((CASE WHEN "Imp_Value"::int != '0' THEN "Imp_Value" ELSE null END)::int) improvement_value,
	max((CASE WHEN "total_Value"::int != '0' THEN "total_Value" ELSE null END)::int) total_value,
	bool_or(substring(imp_class for 1) in ('2','9')) as residential,
        max(nullif(age,'000')::int) as age,
	array_agg(distinct imp_class) as classes,
	array_agg(distinct substring(imp_class for 1)) as class_types
from input.assessor
where city = 'CHICAGO'
group by substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix

);

alter table aux.assessor_summary add unique (address);

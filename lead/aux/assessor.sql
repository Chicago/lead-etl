drop table if exists aux.assessor;

create table aux.assessor as (

select substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix as address,
    sum((substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix = taxpayer_address)::int) owner_occupied,
    count(*) count,
    max(nullif("land_AV"::int,0)) land_value,
    max(nullif("Imp_Value"::int,0)) improved_value,
    max(nullif("total_Value"::int,0)) total_value,
    max(nullif(age::int,0)) max_age,
    min(nullif(age::int,0)) min_age,
    max(no_apt::int) apartments,
    max(nullif(rooms::int, 0)) rooms,
    max(nullif(num_bed::int,0)) beds,
    max(nullif(num_full_baths::int + num_half_baths::int, 0)) as baths,
    max(nullif(bldg_sq_ft::int, 0)) building_area,
    max(nullif(land_sq_ft::int,0)) land_area,

    array_agg(distinct imp_class) as classes,
    array_agg(distinct substring(imp_class for 1)) as class_types,

    -- class codes http://www.cookcountyassessor.com/forms/classcode.PDF
    sum( (substring(imp_class for 1) in ('2','3','9'))::int ) as residential,
    sum( (substring(imp_class for 1) in ('6','7','8','9'))::int ) as incentive,
    sum( (substring(imp_class for 1) in ('3','9'))::int ) as multifamily,
    sum( (substring(imp_class for 1) in ('6'))::int ) as brownfield,
    sum( (substring(imp_class for 1) in ('4'))::int ) as nonprofit,
    sum( (imp_class in ('550','580','581','583','587','589','593') or substring(imp_class for 1) = '8')::int) as industrial,
    sum( (imp_class in ('500','535','501','516','517','522','523','526','527','528','529','530', '531','532','533','535','590','591','592','597','599') or substring(imp_class for 1) = '7')::int ) as commercial

from input.assessor
where city = 'CHICAGO'
group by substring(house_num from 6)::int || ' ' || st_dir || ' ' || st_name || ' ' || st_suffix

);

alter table aux.assessor add unique (address);

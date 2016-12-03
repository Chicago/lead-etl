drop table if exists discontinuity.buildings;

create table discontinuity.buildings as (
with addresses as (
    select *
    from discontinuity.max_bll_under1
    join discontinuity.addresses using (kid_id)
    join output.addresses using (address_id)
    left join aux.buildings using (building_id)
    left join aux.assessor using (address)
    where first_sample_address
),

years_built as (
    select kid_id, 
        min(year_built) buildings_year_built_min, 
        avg(year_built) buildings_year_built_mean, 
        max(year_built) buildings_year_built_max
    from (select kid_id, unnest(years_built) year_built 
          from addresses) t
    group by 1
)

select years_built.*, 
    condition_sound_prop buildings_condition_sound_prop, 
    condition_major_prop buildings_condition_major_prop,
    condition_minor_prop buildings_condition_minor_prop,
    condition_uninhabitable_prop buildings_condition_uninhabitable_prop,
    units buildings_units,

    land_value assessor_land_value,
    improved_value assessor_improved_value,
    max_age assessor_max_age,
    min_age assessor_min_age,
    apartments assessor_apartments,
    owner_occupied*1.0 / count as assessor_owner_occupied

from addresses
left join years_built using (kid_id)

);

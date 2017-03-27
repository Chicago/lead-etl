drop table if exists aux.kids;

create table aux.kids as (

select kid_id, 
    mode() WITHIN GROUP (order by first_name) as first_name, 
    mode() WITHIN GROUP (order by last_name) as last_name,
    mode() WITHIN GROUP (order by sex) as sex,

    -- take the mode date of birth
    -- if a birth date doesn't make sense, exclude it from the average
    mode() WITHIN GROUP (order by CASE WHEN date_of_birth::date <= NOW() THEN date_of_birth::date END) as date_of_birth

from dedupe.infants join dedupe.entity_map using (id)
group by kid_id
);

alter table aux.kids add primary key (kid_id);

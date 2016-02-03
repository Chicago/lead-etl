drop table if exists aux.kids;

create table aux.kids as (

select kid_id, mode(first_name) as first_name, mode(last_name) as last_name,

-- take the average date of birth (postgresql doesn't have avg(date), so cast to epoch and back)
-- if a birth date doesn't make sense, exclude it from the average
to_timestamp(mode(extract(epoch from 
    (CASE WHEN date_of_birth::date > NOW() THEN null ELSE date_of_birth END)::date)))::date as date_of_birth

from dedupe.infants join dedupe.entity_map using (id)
group by kid_id
);

alter table aux.kids add primary key (kid_id);

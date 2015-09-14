drop table if exists aux.name_frequencies;

create table aux.name_frequencies as (

select first_name, count(*), true as first from aux.tests group by first_name
UNION ALL
select last_name, count(*), false from aux.tests group by last_name

);

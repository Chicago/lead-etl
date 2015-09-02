drop table if exists aux.name_frequencies;

create table aux.name_frequencies as (

select first_name, count(*)*sum(num_tests), true as first from aux.kids_initial group by first_name
UNION ALL
select last_name, count(*)*sum(num_tests), false from aux.kids_initial group by last_name

);

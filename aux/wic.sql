drop table if exists aux.wic;

create table aux.wic as (
    select first_name,last_name,date_of_birth
    from input.wic group by first_name, last_name, date_of_birth
);

alter table aux.wic add column id serial primary key;

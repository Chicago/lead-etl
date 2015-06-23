create table aux.immunization_kids as (select first_name, last_name, date_of_birth from input.immunizations group by first_name, last_name, date_of_birth);

drop table if exists aux.wic_kids;

create table aux.wic_kids as (

select w.id wic_id, kt.kid_id kid_id

from aux.tests t join aux.wic w using (first_name,last_name,date_of_birth) 
join aux.kid_tests kt on kt.test_id = t.id

group by w.id, kt.kid_id

);


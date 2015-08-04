drop table if exists aux.wic_kids;

create table aux.wic_kids as (

select w.id wic_id, kt.kid_id kid_id

from aux.tests t join aux.wic w using (first_name,last_name,date_of_birth) 
join aux.kid_tests kt on kt.test_id = t.id

group by w.id, kt.kid_id

);

with wic_unmatched as (
select w.id id, 
substring(first_name for 1) || substring(last_name for 1) as initials,
replace(first_name || last_name || date_of_birth::text, ' ', '') as key from aux.wic w left join aux.wic_kids wk on w.id = wk.wic_id where wk.wic_id is null
)

insert into aux.wic_kids (wic_id, kid_id) (

select w.id, min(kc.id1) from wic_unmatched w left join aux.kids_initial k on k.initials = w.initials and levenshtein_less_equal(w.key, k.key, 1) < 2 
join aux.kid_components kc on k.id = kc.id2
group by w.id

);

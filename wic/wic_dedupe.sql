DROP TABLE if exists wic.wic_kids_original;

CREATE TABLE wic.wic_kids_original AS (
    SELECT cur_frst_t first_name, cur_last_t last_name, birth_d::date date_of_birth
    FROM wic.wic_infant group by cur_frst_t, cur_last_t, birth_d
);

ALTER TABLE wic.wic_kids_original ADD id SERIAL PRIMARY KEY;

drop table if exists wic.wic_kid_edges;

create table wic.wic_kid_edges as (

select w.id wic_id, kt.kid_id kid_id, min(substring(t.first_name for 1) || substring(t.last_name for 1)) as initials

from aux.tests t join wic.wic_kids_original w using (first_name,last_name,date_of_birth)
join aux.kid_tests kt on kt.test_id = t.id

group by w.id, kt.kid_id

);

with wic_unmatched as (
select w.id id,
substring(first_name for 1) || substring(last_name for 1) as initials,
replace(first_name || last_name || date_of_birth::text, ' ', '') as key from wic.wic_kids_original w left join wic.wic_kid_edges wk on w.id = wk.wic_id where wk.wic_id is null
)

insert into wic.wic_kid_edges (wic_id, kid_id, initials) (

select w.id, kc.id1, k.initials from wic_unmatched w left join aux.kids_initial k on k.initials = w.initials and levenshtein_less_equal(w.key, k.key, 1) < 2
join aux.kid_components kc on k.id = kc.id2

);

drop table if exists wic.wic_edges;

create table wic.wic_edges as (

select w1.wic_id id1, w2.wic_id id2, w1.initials from wic.wic_kid_edges w1 join wic.wic_kid_edges w2 using (kid_id) join aux.kids_initial ki on kid_id = ki.id where w1.wic_id != w2.wic_id

);


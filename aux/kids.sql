drop table if exists aux.kids;

create table aux.kids as (

with test_kids as (
    select kid_id, first_name, last_name, 
    CASE WHEN date_of_birth < sample_date THEN date_of_birth ELSE null END AS date_of_birth
    from aux.kid_tests_info join aux.tests t on test_id = id
),

wic_kids as (
    select kid_id, brth_fst_t first_name, brth_lst_t last_name, birth_d date_of_birth
    from aux.kid_wics join cornerstone.partenrl using (part_id_i)
)

select kid_id, mode(first_name) as first_name, mode(last_name) as last_name,

-- take the average date of birth (postgresql doesn't have avg(date), so cast to epoch and back)
-- if a birth date doesn't make sense, exclude it from the average
to_timestamp(mode(extract(epoch from date_of_birth)))::date as date_of_birth

from (select * from test_kids UNION ALL select * from wic_kids) t
group by kid_id
);

alter table aux.kids add primary key (kid_id);

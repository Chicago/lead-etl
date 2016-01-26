drop table if exists aux.kids;

create table aux.kids as (

select kid_id as id, mode(first_name) as first_name, mode(last_name) as last_name,

-- take the average date of birth (postgresql doesn't have avg(date), so cast to epoch and back)
-- if a birth date doesn't make sense, exclude it from the average
to_timestamp(mode(
	CASE WHEN t.date_of_birth < t.sample_date THEN extract(epoch from t.date_of_birth) ELSE null END
))::date as date_of_birth,

count(distinct test_id) as num_tests,

min(t.sample_date) as min_sample_date,
max(t.sample_date) as max_sample_date,

max(t.bll) as max_bll,
to_timestamp(sum(
    CASE WHEN first_ebll THEN extract(epoch from t.sample_date) ELSE null END))::date as first_ebll_date

from aux.kid_tests_info kt
join aux.tests t on kt.test_id = t.id
group by kt.kid_id
);

alter table aux.kids add primary key (id);

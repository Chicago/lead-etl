-- https://wiki.postgresql.org/wiki/Aggregate_Mode

CREATE OR REPLACE FUNCTION _final_mode(anyarray)
  RETURNS anyelement AS
$BODY$
    SELECT a
    FROM unnest($1) a
    GROUP BY 1 
    ORDER BY COUNT(1) DESC, 1
    LIMIT 1;
$BODY$
LANGUAGE 'sql' IMMUTABLE;
 
-- Tell Postgres how to use our aggregate
DROP AGGREGATE IF EXISTS mode(anyelement);

CREATE AGGREGATE mode(anyelement) (
  SFUNC=array_append, --Function to call for each row. Just builds the array
  STYPE=anyarray,
  FINALFUNC=_final_mode, --Function to call after everything has been added to array
  INITCOND='{}' --Initialize an empty array when starting
);

drop table if exists aux.kids;

create table aux.kids as (

select kt.kid_id as id, min(t.first_name) as first_name ,min(t.last_name) as last_name,

-- take the average date of birth (postgresql doesn't have avg(date), so cast to epoch and back)
-- if a birth date doesn't make sense, exclude it from the average
to_timestamp(mode(
	CASE WHEN t.date_of_birth < t.sample_date THEN extract(epoch from t.date_of_birth) ELSE null END
))::date as date_of_birth,
-- TODO: count distinct spellings
count(*) as num_tests,
max(minmax::int*test_number) as minmax_test_number,
min(t.sample_date) as min_sample_date,
max(t.sample_date) as max_sample_date,

max(t.bll) as max_bll,
to_timestamp(max(kt.max::int * extract(epoch from t.sample_date)))::date as max_date,

max(kt.minmax::int*t.bll) as minmax_bll,
to_timestamp(max(kt.minmax::int * extract(epoch from t.sample_date)))::date as minmax_date

from aux.kid_tests kt
join aux.tests t on kt.test_id = t.id
group by kt.kid_id
);

alter table aux.kids add primary key (id);

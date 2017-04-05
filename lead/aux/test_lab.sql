drop table if exists aux.test_lab;

create table aux.test_lab as (
    with test_lab as (
        select test_id, lab_id, CASE WHEN lab_id ~ '^\s*\d+$' THEN lab_id::int END as idph_lab_id
        from aux.tests
    )
    select test_id, coalesce(solar_lab_id, lab_id) as lab_id
    from test_lab left join input.labs using (idph_lab_id)
);

alter table aux.test_lab add primary key (test_id);

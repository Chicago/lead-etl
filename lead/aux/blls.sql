drop table if exists aux.blls;

create table aux.blls as (
    select test_id, bll as bll0, 
        CASE WHEN l.count >= 50 and l.limit > 1 and l.limit = bll 
            -- coalesce because sometimes there is no entry in bll_months
            THEN coalesce(mean, bll) ELSE bll END as bll,
        CASE WHEN l.count >= 50 THEN l.limit END as lod,
        CASE WHEN l.count >= 50 THEN
            not (l.limit = bll and l.limit > 1) END as detected
    FROM aux.tests t
    LEFT JOIN aux.lab_months l on
        l.lab_id = t.lab_id and
        l.sample_type = t.sample_type and
        l.month = date_trunc('month', sample_date)
    LEFT JOIN aux.bll_months using (month, bll)
);

ALTER TABLE aux.blls ADD PRIMARY KEY (test_id);

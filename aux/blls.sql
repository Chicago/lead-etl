drop table if exists aux.blls;

create table aux.blls as (
    select test_id, bll as bll0,
        CASE WHEN l.count >= 50 and bll_percentiles[1] > 1 and bll_percentiles[1] = bll THEN bll/2.0 ELSE bll END as bll,

        CASE WHEN l.count >= 50 THEN bll_percentiles[1] END as lod,
        CASE WHEN l.count >= 50 THEN
            (bll_percentiles[1] != bll or bll_percentiles[1] = 1) END as detected

    FROM aux.tests t
    LEFT JOIN  output.lab_months l on
        l.lab_id = t.lab_id and
        l.sample_type = t.sample_type and
        l.month = date_trunc('month', sample_date)
);

ALTER TABLE aux.blls ADD PRIMARY KEY (test_id);

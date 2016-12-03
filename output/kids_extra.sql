drop table if exists output.kids_extra;

create table output.kids_extra as (
    with 
    
    tests as (
         select *, true as venal from output.tests where sample_type='V'
         UNION ALL
         select *, false as venal from output.tests
    ),
    
    tests_detected_over1 as (
        select kid_id, venal, address_id, date, bll, lab_id, sample_type, age,
        coalesce(lag(date) OVER (PARTITION BY kid_id,venal order by date asc), date) as last_date,
        coalesce(lag(bll) OVER (PARTITION BY kid_id,venal order by date asc), bll) as last_bll
        --from output.tests t join aux.kids using (kid_id)
        from tests
        where detected and age > 365
    ),

    tests_detected_over1_agg as (
        select kid_id, venal,
            (CASE WHEN min(last_date) != max(date) THEN
                sum((date - last_date)*(last_bll +(bll - last_bll)/2.0)) END) / 365 as cumulative_bll_over1,

            (max(date) - min(last_date))/365.0 as bll_years_over1

        from tests_detected_over1
        group by 1,2
    ),

    tests_detected_agg as (
        select kid_id, venal,
            array_remove(array_agg(distinct CASE WHEN age <= 1*365 THEN address_id END), null)
                as addresses_under1,
            max(CASE WHEN age <= 1*365 THEN bll END) max_bll_under1,
            max(CASE WHEN age > 1*365 THEN bll END) max_bll_over1,
            max(CASE WHEN age between 366 and 4*365 THEN bll END) max_bll_over1_under4,

            min(CASE WHEN age <= 1*365 THEN bll END) min_bll_under1,
            min(CASE WHEN age > 1*365 THEN bll END) min_bll_over1,
            min(CASE WHEN age between 366 and 4*365 THEN bll END) min_bll_over1_under4,

            avg(CASE WHEN age > 365 THEN bll END) as avg_bll_over1,
            avg(CASE WHEN age <= 365 THEN bll END) as avg_bll_under1,
            avg(CASE WHEN age between 366 and 4*365 THEN bll END) avg_bll_over1_under4,

            count(CASE WHEN age > 1*365 THEN bll END) count_bll_over1,
            count(CASE WHEN age <= 1*365 THEN bll END)count_bll_under1,
            count(CASE WHEN age between 366 and 4*365 THEN bll END) count_bll_over1_under4,

            max(CASE WHEN age <= 1*365 THEN date END) as last_date_under1,
            max(CASE WHEN age > 1*365 THEN date END) as last_date_over1,
            max(CASE WHEN age between 366 and 4*365 THEN date END) last_date_over1_under4

        from tests
        where detected
        group by 1,2
    ),

    last_blls as (
        select kid_id, venal, 
            max(CASE WHEN age <= 365 and last_date_under1 = date THEN bll END)
                as last_bll_under1,
            max(CASE WHEN age > 365 and last_date_over1 = date THEN bll END)
                as last_bll_over1,
            max(CASE WHEN age between 366 and 4*365 and last_date_over1_under4 = date THEN bll END)
                as last_bll_over1_under4
        from tests join tests_detected_agg using (kid_id, venal)
        where detected
        group by 1,2
    ),

    detected as (
        select kid_id, coalesce(sample_type = 'V', false) as venal,
            avg(CASE WHEN age <= 365 THEN detected::int END) = 1 detected_under1,
            avg(CASE WHEN age > 365 THEN detected::int END) = 1 detected_over1
        from tests
        group by 1,2
    )

    select *, 
        -- when only one test or all on same date, use avg bll
        coalesce(CASE WHEN bll_years_over1 > 0 THEN cumulative_bll_over1 / bll_years_over1 END, avg_bll_over1) as avg_cumulative_bll_over1
    from tests_detected_over1_agg
    full outer join tests_detected_agg using (kid_id, venal)
    full outer join last_blls using (kid_id, venal)
    full outer join detected using (kid_id, venal)
);

alter table output.kids_extra add primary key (kid_id, venal);

drop table if exists discontinuity.first_bll6_extra;

create table discontinuity.first_bll6_extra as (
    with 
    
    tests as (
        select * from
         (select *, true as venal from output.tests where sample_type='V'
         UNION ALL
         select *, false as venal from output.tests) t
        join output.kids using (kid_id)
        where first_bll6_sample_date is not null

    ),
    
    tests_detected_over1 as (
        select kid_id, venal, address_id, date, bll, lab_id, sample_type, age,
        coalesce(lag(date) OVER (PARTITION BY kid_id,venal order by date asc), date) as last_date,
        coalesce(lag(bll) OVER (PARTITION BY kid_id,venal order by date asc), bll) as last_bll
        --from output.tests t join aux.kids using (kid_id)
        from tests
        where date > first_bll6_sample_date
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
            array_remove(array_agg(distinct CASE WHEN date <= first_bll6_sample_date THEN address_id END), null)
                as addresses_under1,
            max(CASE WHEN date <= first_bll6_sample_date THEN bll END) max_bll_under1,
            max(CASE WHEN date > first_bll6_sample_date THEN bll END) max_bll_over1,

            min(CASE WHEN date <= first_bll6_sample_date THEN bll END) min_bll_under1,
            min(CASE WHEN date > first_bll6_sample_date THEN bll END) min_bll_over1,

            avg(CASE WHEN date > first_bll6_sample_date THEN bll END) as avg_bll_over1,
            avg(CASE WHEN date <= first_bll6_sample_date THEN bll END) as avg_bll_under1,

            count(CASE WHEN date > first_bll6_sample_date THEN bll END) sample_count_over1,
            count(CASE WHEN date <= first_bll6_sample_date THEN bll END) sample_count_under1,

            max(CASE WHEN date <= first_bll6_sample_date THEN date END) as last_sample_date_under1,
            max(CASE WHEN date > first_bll6_sample_date THEN date END) as last_sample_date_over1
        from tests
        group by 1,2
    ),

    last_blls as (
        select kid_id, venal, 
            max(CASE WHEN date <= first_bll6_sample_date and last_sample_date_under1 = date THEN bll END)
                as last_bll_under1,
            max(CASE WHEN date > first_bll6_sample_date and last_sample_date_over1 = date THEN bll END)
                as last_bll_over1
        from tests join tests_detected_agg using (kid_id, venal)
        group by 1,2
    ),

    detected as (
        select kid_id, coalesce(sample_type = 'V', false) as venal,
            avg(CASE WHEN date <= first_bll6_sample_date THEN detected::int END) = 1 detected_under1,
            avg(CASE WHEN date > first_bll6_sample_date THEN detected::int END) = 1 detected_over1
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

alter table discontinuity.first_bll6_extra add primary key (kid_id, venal);

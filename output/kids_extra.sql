drop table if exists output.kids_extra;

create table output.kids_extra as (
    with bll_windows as (
        select kid_id, false as venal, date, bll, lab_id, sample_type, age,
        coalesce(lag(date) OVER (PARTITION BY kid_id order by date asc), date_of_birth) as last_date,
        coalesce(lag(bll) OVER (PARTITION BY kid_id order by date asc), 0) as last_bll
        from output.tests join aux.kids using (kid_id)
    )
    ,
    vbll_windows as (
        select kid_id, true as venal, date, bll, lab_id, sample_type, age,
        coalesce(lag(date) OVER (PARTITION BY kid_id order by date asc), date_of_birth) as last_date,
        coalesce(lag(bll) OVER (PARTITION BY kid_id order by date asc), 0) as last_bll
        from output.tests join aux.kids using (kid_id)
        where sample_type = 'V'
    ),

    kids_extra as (
        select kid_id, venal,
            array_agg(l.lab_id) as labs,
            count(*) as test_count,

            max(mode_bll) as lod,
            max(CASE WHEN age < 1*375 THEN mode_bll END) as lod_under1,
            
            max(CASE WHEN age < 1*375 THEN bll END) max_bll_under1,

            max(CASE WHEN age >= 1*375 THEN bll END) max_bll_over1,
            max(CASE WHEN age >= 2*365 THEN bll END) max_bll_over2,
            max(CASE WHEN age >= 3*365 THEN bll END) max_bll_over3,
            
            min(CASE WHEN age >= 1*375 THEN bll END) min_bll_over1,
            min(CASE WHEN age >= 2*365 THEN bll END) min_bll_over2,
            min(CASE WHEN age >= 3*365 THEN bll END) min_bll_over3,

            max(bll) as max_bll,
            min(bll) as min_bll,

            avg(bll) as avg_bll,
            avg(CASE WHEN age < 375 THEN bll END) as avg_bll_over1,

            (CASE WHEN min(last_date) != max(date) THEN
                sum((date - last_date)*(last_bll +(bll - last_bll)/2.0))
            END) / 365 as cumulative_bll,
            (max(date) - min(last_date))/365.0 as bll_years,

            (CASE WHEN min(last_date) != max(date) THEN
                sum(CASE WHEN age >= 375
                    THEN (date - last_date)*(last_bll +(bll - last_bll)/2.0) 
            END) END) / 365 as cumulative_bll_over1,
            (max(CASE WHEN age >= 375 THEN date END) 
                - min(CASE WHEN age >= 375 THEN last_date END))/365.0 as bll_years_over1

        from (select * from bll_windows UNION ALL select * from vbll_windows) t
        join output.lab_years l on 
            l.lab_id = t.lab_id and 
            l.year = extract(year from date) and 
            l.sample_type = t.sample_type
        where l.test_count > 1000
        group by kid_id, venal
    )

    select *, 
        CASE WHEN bll_years > 0 THEN cumulative_bll / bll_years END 
            as avg_cumulative_bll,
        CASE WHEN bll_years_over1 > 0 THEN cumulative_bll_over1 / bll_years_over1 END 
            as avg_cumulative_bll_over1
    from kids_extra
);

alter table output.kids_extra add primary key (kid_id, venal);

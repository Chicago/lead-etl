drop table if exists output.kids_extra;

create table output.kids_extra as (
    select kid_id,
        max(CASE WHEN AGE < 365*1 THEN bll END) max_bll_under1,
        max(CASE WHEN AGE < 365*2 THEN bll END) max_bll_under2,
        max(CASE WHEN AGE < 365*3 THEN bll END) max_bll_under3,
        max(CASE WHEN AGE < 365*4 THEN bll END) max_bll_under4,
        max(CASE WHEN AGE >= 365*1 THEN bll END) max_bll_over1,
        max(CASE WHEN AGE >= 365*2 THEN bll END) max_bll_over2,
        max(CASE WHEN AGE >= 365*3 THEN bll END) max_bll_over3,
        max(CASE WHEN AGE >= 365*4 THEN bll END) max_bll_over4,
        max(CASE WHEN first THEN bll END) first_bll
    from output.tests
    join output.labs using (lab_id)
    where sample_type = 'V'
    and mode_bll = 1
    group by kid_id
);

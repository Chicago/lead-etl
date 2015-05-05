drop table if exists output.kids;

create table output.kids as (
select
        k.id kid_id,
        --k.first_name kid_first_name,
        --k.last_name kid_last_name,
        k.date_of_birth kid_date_of_birth,
        
        e.surname_null kid_surname_null,
        e.surname_ethnicity surname_ethnicity,
        e.kid_ethnicity kid_ethnicity,

        t.sex kid_sex,
        t.id test_id,
        t.sample_date test_date,
        date_part('year', t.sample_date) as year,
        t.sample_date - k.date_of_birth test_kid_age_days,
        t.bll test_bll,
        
        t.minmax test_minmax,
        t.min test_min,
        t.test_number,
        k.minmax_bll,
        k.min_sample_date,
        
        t.address_method,
        st_x(t.geom) address_lat,
        st_y(t.geom) address_lng,
        
        t.address_id address_id,
        t.census_tract_id,
        t.community_area_id,
        t.ward_id,

--	ti.test_id is null as address_inspection_null,
		--ti.count address_inspection_count,
--        ti.hazard_int address_inspection_hazard_int,
--        ti.hazard_ext address_inspection_hazard_ext,
        
--        ti.min_init_date address_inspection_init_date,
--        ti.min_comply_date address_inspection_comply_date,
        --ti.max_init_date address_inspection_max_init_date,
        --ti.max_comply_date address_inspection_max_comply_date,
        
--        tt.count address_test_count,
--        tt.kid_count address_test_kid_count,
--        tt.ebll_test_count address_test_ebll_test_count,
--		tt.ebll_test_ratio address_test_ebll_test_ratio,
--		tt.avg_ebll address_test_avg_ebll,
--		tt.ebll_kid_count address_test_ebll_kid_count,
--		tt.ebll_kid_ratio address_test_ebll_kid_ratio,
        

		bd.address is null address_building_null,
		bd.year_built address_building_year,
        bd.year_built <= 1978 as address_building_pre1978,
        bd.bldg_condi address_building_condition,
        bd.units address_building_units,
        bd.stories address_building_stories,
        bd.vacant address_building_vacant,

		ass.address is null address_assessor_null,
        ass.total_value address_assessor_total_value,
        ass.age address_assessor_age
from aux.kids k
join aux.tests_geocoded t on k.id = t.kid_id
left join aux.kid_ethnicity e on k.id = e.kid_id
left join aux.address_inspections ti on ti.test_id = t.id
left join aux.address_tests tt on tt.test_id = t.id
left join aux.buildings_summary bd on
    t.address = bd.address
left join aux.assessor_summary ass on
	t.address = ass.address
);

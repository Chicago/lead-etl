CREATE TEMP VIEW dedupe AS (

WITH infants as (

select part_id_i
FROM  cornerstone.partenrl
join cornerstone.partpgm using (part_id_i)
where category_c='I'
group by 1
)

SELECT array_agg(test_id) as test_ids, null as cornerstone_ids, first_name, last_name, date_of_birth, 
    coalesce(geocode_address, clean_address) as address, count(*) as count
FROM aux.tests group by 3,4,5,6

UNION ALL

SELECT null, array_agg(distinct part_id_i), 
    brth_fst_t, brth_lst_t, birth_d, addr_ln1_t, count(*) as count
from 
infants join
cornerstone.partenrl using (part_id_i)
left join cornerstone.partaddr a on part_id_i = addr_id_i
group by 3,4,5,6);

\COPY (select * from dedupe) TO STDOUT WITH CSV HEADER;

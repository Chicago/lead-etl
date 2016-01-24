CREATE TEMP VIEW dedupe AS ( SELECT array_agg(id) as test_ids, null as cornerstone_ids, first_name, last_name, mi, date_of_birth, clean_address2 as address, count(*) as count
FROM aux.tests group by 3,4,5,6,7
UNION ALL
SELECT null, array_agg(distinct part_id_i), brth_fst_t, brth_lst_t, brth_mi_t, birth_d, addr_ln1_t, count(*) as count
from cornerstone.partenrl 
join cornerstone.partaddr on part_id_i = addr_id_i
join cornerstone.partpgm using (part_id_i)
where category_c='I'
group by 3,4,5,6,7);

\COPY (select * from dedupe) TO STDOUT WITH CSV HEADER;

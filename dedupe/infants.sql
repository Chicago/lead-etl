DROP TABLE IF EXISTS dedupe.infants;

CREATE TABLE dedupe.infants AS (

WITH infants as (

select part_id_i
FROM  cornerstone.partenrl
join cornerstone.partpgm using (part_id_i)
where category_c='I'
group by 1
),

infants2 as (
SELECT test_id, null as cornerstone_id, first_name, last_name, 
    sex, date_of_birth::text, date_of_birth-'1970-01-01' as day,
    coalesce(geocode_address, clean_address) as address
FROM aux.tests 
UNION ALL
SELECT null, part_id_i,
    brth_fst_t, brth_lst_t, sex_c, birth_d::text, birth_d-'1970-01-01' as day,
    addr_ln1_t
from 
infants join
cornerstone.partenrl using (part_id_i)
left join cornerstone.partaddr a on part_id_i = addr_id_i
)

select first_name, last_name, date_of_birth, sex, day, address, count(*) as count,
array_remove(array_agg(test_id), null) test_ids, 
array_remove(array_agg(cornerstone_id), null) cornerstone_ids
from infants2
where first_name is not null and last_name is not null and date_of_birth is not null
group by 1,2,3,4,5,6

);

alter table dedupe.infants add column id serial primary key;

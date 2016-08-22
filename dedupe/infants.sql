DROP TABLE IF EXISTS dedupe.infants;

CREATE TABLE dedupe.infants AS (

-- get participant ids of wic infants
WITH wic_infants as (
    select part_id_i
    FROM cornerstone.partpgm
    where category_c='I'
    group by 1
),

infants as (
    -- tests
    SELECT test_id, null::text as cornerstone_id, null::int as icare_id,
        first_name, last_name, sex, date_of_birth, 
        coalesce(geocode_address, clean_address) as address
    FROM aux.tests 
    UNION ALL
    -- cornerstone
    SELECT null, part_id_i, null,
        brth_fst_t, brth_lst_t, sex_c, birth_d, addr_ln1_t
    from 
    wic_infants join
    cornerstone.partenrl using (part_id_i)
    left join cornerstone.partaddr a on part_id_i = addr_id_i
    UNION ALL
    -- icare
    SELECT null, null, icare_id,
        first_name, last_name, sex, date_of_birth, address
    FROM input.icare
)

-- unaccent text fields for dedupe
select unaccent(first_name) first_name, 
    unaccent(last_name) last_name, 
    date_of_birth::text, 
    unaccent(sex) sex, 
    unaccent(address) address, 
    min(date_of_birth) - '1970-01-01' as day, count(*) as count,
    array_remove(array_agg(test_id), null) test_ids, 
    array_remove(array_agg(cornerstone_id), null) cornerstone_ids,
    array_remove(array_agg(icare_id), null) icare_ids
from infants
where first_name is not null and last_name is not null and date_of_birth is not null
group by 1,2,3,4,5

);

alter table dedupe.infants add column id serial primary key;

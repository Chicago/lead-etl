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
    SELECT test_id, 
            null::text as cornerstone_id, 
            null::int as stellar_id,
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
    -- stellar
    SELECT null, null, child_id,
        name_first, name_last, sex, dob_child, upper(assemaddr)
    FROM stellar.child
    JOIN (select addr_id, child_id FROM stellar.ca_link group by 1,2) ca 
        using (child_id)
    JOIN stellar.addr using (addr_id)
)

-- unaccent text fields for dedupe
-- remove non-alpha chars (including spaces) from names
-- also remove that unicode character from that address!
select regexp_replace(upper(unaccent(first_name)), '[^A-Z]', '', 'g') first_name, 
    regexp_replace(upper(unaccent(last_name)), '[^A-Z]', '', 'g') last_name, 
    date_of_birth::text, 
    unaccent(sex) sex, 
    regexp_replace(unaccent(address), '[\x80-\xFF]', '', 'g') as address, 
    min(date_of_birth) - '1970-01-01' as day, count(*) as count,
    array_remove(array_agg(test_id), null) test_ids, 
    array_remove(array_agg(cornerstone_id), null) cornerstone_ids,
    array_remove(array_agg(stellar_id), null) stellar_ids
from infants
where first_name is not null and last_name is not null and date_of_birth is not null
group by 1,2,3,4,5

);

alter table dedupe.infants add column id serial primary key;

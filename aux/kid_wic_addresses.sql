DROP TABLE IF EXISTS aux.kid_wic_addresses;

CREATE TABLE aux.kid_wic_addresses AS (
    -- keys to link cornerstone addresses to aux.addresses
    WITH wic_addresses AS (select geocode_address as address, unnest(ogc_fids) as ogc_fid FROM cornerstone.addresses),

    -- collect linked addresses 
    addresses AS (
        SELECT part_id_i, address_id, pa.last_upd_d, register_d
        FROM cornerstone.partaddr pa
        JOIN wic_addresses USING (ogc_fid)
        JOIN aux.addresses a USING (address)
        JOIN cornerstone.partenrl ON addr_id_i = part_id_i
    ),

    -- find first address for each participant id
    first_address AS (
        SELECT part_id_i, min(last_upd_d) last_upd_d
        FROM addresses
        GROUP BY part_id_i
    ),

    -- replace last_upd_d with register_d for first address
    addresses2 AS (
        SELECT part_id_i, address_id, a.register_d
        FROM addresses a JOIN first_address d using (part_id_i, last_upd_d)
    ),

    -- take unique rows from addresses and addresses2
    all_addresses AS (
        SELECT part_id_i, address_id, last_upd_d as date
        FROM addresses
        UNION
        SELECT part_id_i, address_id, register_d as date
        FROM addresses2
    ),

    -- get addresses through mother
    mother_addresses AS (
        SELECT k.part_id_i, a.address_id,
                greatest(a.date, min_visit_date) as date, k.mothr_id_i
        FROM aux.kid_mothers k
        JOIN all_addresses a
        ON mothr_id_i = a.part_id_i
    )

    SELECT kid_id, a.*
    FROM (SELECT *, null as mothr_id_i FROM all_addresses i
        UNION SELECT * FROM mother_addresses) a
    JOIN aux.kid_wics USING (part_id_i)
    JOIN aux.kids using (kid_id)
    WHERE date_of_birth - date < 365
);

create index on aux.kid_wic_addresses (kid_id, address_id);

DROP TABLE IF EXISTS aux.kid_wic_addresses;

CREATE TABLE aux.kid_wic_addresses AS (
    -- keys to link cornerstone addresses to aux.addresses
    WITH wic_addresses AS (select address, unnest(ogc_fids) as ogc_fid FROM cornerstone.addresses),

    -- collect linked addresses 
    addresses AS (
        SELECT part_id_i, a.id AS address_id, pa.last_upd_d, register_d
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
        SELECT part_id_i, address_id,
            CASE WHEN d.part_id_i is null THEN a.last_upd_d ELSE a.register_d END AS min_date,
        a.last_upd_d as max_date
        FROM addresses a LEFT JOIN first_address d using (part_id_i, last_upd_d)
    )

    SELECT kid_id, address_id, min(min_date) as min_date, max(max_date) as max_date, count(*) as num_records
    FROM addresses2
    JOIN aux.kid_wics USING (part_id_i)
    GROUP BY kid_id, address_id
);

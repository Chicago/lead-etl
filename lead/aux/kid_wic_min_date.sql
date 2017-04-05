DROP TABLE IF EXISTS aux.kid_wic_min_date;

CREATE TABLE aux.kid_wic_min_date AS (
SELECT kid_id, least(
    -- discard prenatal nonsense prenatal entries
    min(CASE WHEN date_of_birth - visit_d < 365 THEN visit_d END), 
    min(register_d), min(partenrl.last_upd_d), min(partaddr.last_upd_d)) as date
FROM aux.kid_wics
JOIN aux.kids using (kid_id)
JOIN cornerstone.partenrl using (part_id_i)
LEFT JOIN cornerstone.partaddr on part_id_i = addr_id_i
LEFT JOIN cornerstone.birth using (part_id_i)
LEFT JOIN cornerstone.prenatl on birth.mothr_id_i = prenatl.part_id_i
GROUP BY 1
);

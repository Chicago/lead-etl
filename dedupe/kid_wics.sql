DROP TABLE IF EXISTS aux.kid_wics;

CREATE TABLE aux.kid_wics AS (
SELECT t.part_id_i, kid_id, least(
    -- discard prenatal nonsense prenatal entries
    min(CASE WHEN birth_d - visit_d between -365 and 365 THEN visit_d END), 
    min(register_d), min(partenrl.last_upd_d)) as date
FROM (SELECT unnest(cornerstone_ids) part_id_i, id FROM dedupe.infants where cornerstone_ids is not null) t
JOIN dedupe.entity_map USING (id)
JOIN cornerstone.partenrl using (part_id_i)
LEFT JOIN cornerstone.birth using (part_id_i)
LEFT JOIN cornerstone.prenatl on prenatl.part_id_i = birth.mothr_id_i
GROUP BY 1,2
);

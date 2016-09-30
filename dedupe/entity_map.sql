DROP TABLE IF EXISTS dedupe.entity_map;

CREATE TABLE dedupe.entity_map AS (
    SELECT COALESCE(id1, canon_id, id) as kid_id, id
    FROM dedupe.infants LEFT JOIN dedupe.entity_map0 USING (id) LEFT JOIN dedupe.exact_matches on COALESCE(canon_id, id) = id2
)

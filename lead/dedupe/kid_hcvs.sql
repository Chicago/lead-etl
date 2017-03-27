DROP TABLE IF EXISTS aux.kid_hcvs;

CREATE TABLE aux.kid_hcvs AS (

SELECT hcv_id, kid_id
FROM (SELECT unnest(hcv_ids) hcv_id, id FROM dedupe.infants where hcv_ids is not null) t
      JOIN dedupe.entity_map USING (id)

);

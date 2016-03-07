DROP TABLE IF EXISTS aux.kid_wics;

CREATE TABLE aux.kid_wics AS (

SELECT part_id_i, kid_id
FROM (SELECT unnest(cornerstone_ids) part_id_i, id FROM dedupe.infants where cornerstone_ids is not null) t
      JOIN dedupe.entity_map USING (id)
GROUP BY 1,2
);

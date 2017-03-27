DROP TABLE IF EXISTS aux.kid_stellars;

CREATE TABLE aux.kid_stellars AS (

SELECT stellar_id, kid_id
FROM (SELECT unnest(stellar_ids) stellar_id, id FROM dedupe.infants where stellar_ids is not null) t
      JOIN dedupe.entity_map USING (id)
group by 1,2
);

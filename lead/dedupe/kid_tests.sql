DROP TABLE IF EXISTS aux.kid_tests;

CREATE TABLE aux.kid_tests AS (

SELECT test_id, kid_id
FROM (SELECT unnest(test_ids) test_id, id FROM dedupe.infants where test_ids is not null) t
      JOIN dedupe.entity_map USING (id)

);

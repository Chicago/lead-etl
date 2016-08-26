DROP TABLE IF EXISTS aux.kid_icares;

CREATE TABLE aux.kid_icares AS (

SELECT icare_id, kid_id
FROM (
    SELECT unnest(icare_ids) icare_id, id 
    FROM dedupe.infants where icare_ids is not null
) t
JOIN dedupe.entity_map USING (id)
GROUP BY 1,2
);

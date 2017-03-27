DROP TABLE IF EXISTS aux.kid_mothers;

CREATE TABLE aux.kid_mothers AS (
    SELECT kid_id, k.part_id_i, mothr_id_i,
        min(visit_d) as min_visit_date
    FROM cornerstone.birth b
    -- join prenatal on mother's id
    JOIN cornerstone.prenatl p ON b.mothr_id_i = p.part_id_i
    -- join enroll on kid's id
    JOIN cornerstone.partenrl e ON e.part_id_i = b.part_id_i 
    -- join kids
    JOIN aux.kid_wics k on b.part_id_i = k.part_id_i
    JOIN aux.kids using (kid_id)
    -- exclude bad prenatal records
    WHERE date_of_birth - visit_d between -365 and 365
    GROUP BY 1,2,3
);

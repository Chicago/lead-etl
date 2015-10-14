INSERT INTO wic.wic_components (id1, id2) (
    SELECT wko.id, wko.id from wic.wic_kids_original wko left join wic.wic_components wc on wko.id = wc.id2 where wc.id2 is null
);

drop table if exists wic.wic_kids;

CREATE TABLE wic.wic_kids AS (
    select wke.kid_id as kid_id, wi.id as wic_id
    from wic.wic_components wc join wic.wic_kid_edges wke on wc.id1 = wke.wic_id
    join wic.wic_kids_original wko on wke.wic_id = wko.id
    join wic.wic_infant wi on first_name = cur_frst_t and last_name=cur_last_t and birth_d::date = date_of_birth
);

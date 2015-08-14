drop table if exists output.wic;

create table output.wic as (

with wic_kids as (select distinct on (kid_id) kid_id, wic_id from aux.wic_kids)

select wk.kid_id, w.* from wic_kids wk join aux.wic w on wk.wic_id = w.id

);

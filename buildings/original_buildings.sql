drop table if exists buildings.original_buildings;

create temp sequence original_building_id;
SELECT setval('original_building_id', (select max(orig_bldg_)+1 from input.buildings));

create table buildings.original_buildings as (
    select coalesce(nullif(orig_bldg_, 0), nextval('original_building_id')) as orig_bldg_, orig_bldg_ as orig_bldg_2, ogc_fid,
        f_add1,t_add1, coalesce(pre_dir1, '') as pre_dir1, st_name1, coalesce(st_type1, '') as st_type1, 
        edit_date,
        st_transform(st_setsrid(st_point(x_coord,y_coord),3435), 4326) as geom
    from input.buildings
    where st_name1 is not null and bldg_statu='ACTIVE' and non_standa is null
);

drop table if exists buildings.addresses;

create table buildings.addresses as (
    select distinct on (address) address, id, geom, ogc_fid
    from buildings.original_addresses
    order by address, edit_date asc
);

alter table buildings.addresses add unique (address);

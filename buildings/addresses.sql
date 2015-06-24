drop table if exists buildings.addresses;

create table buildings.addresses as (
    select distinct on (address) address, id, geom
    from buildings.original_addresses
    order by address, edit_date asc
);

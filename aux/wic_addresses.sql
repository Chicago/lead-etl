with wic_addresses as (
    select "FULL_ADDR" as address,
    st_transform(st_setsrid(st_point("XCOORD", "YCOORD"),3435), 4326) as geom
    from input.wic_addresses left join aux.addresses on "FULL_ADDR"=address
    where address is null
)

insert into aux.addresses (address, lat 

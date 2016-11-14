drop table if exists aux.kid_stellar_addresses;

create table aux.kid_stellar_addresses as (
    with addresses as (
        select kid_id, address_id, first_occ, last_occ
        from aux.kid_stellars
        join stellar.ca_link on stellar_id = child_id
        join stellar.addr using (addr_id)
        join aux.addresses on address = upper(assemaddr)
    )
    select kid_id, address_id, first_occ as date
    from addresses
    UNION ALL
    select kid_id, address_id, last_occ as date
    from addresses
);

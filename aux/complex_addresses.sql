drop table if exists aux.complex_addresses;

create temp sequence complex_id;
SELECT setval('complex_id', (select max(complex_id)+1 from buildings.complex_buildings));

create table aux.complex_addresses as ( 
    select a.id, coalesce(c.complex_id, nextval('complex_id'))
        from aux.addresses a left join buildings.addresses a2 using (address)
        left join buildings.building_addresses b on a2.id = b.address_id
        left join buildings.complex_buildings c on b.building_id = c.building_id
);


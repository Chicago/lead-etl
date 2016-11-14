drop table if exists aux.kid_hcv_addresses;

create table aux.kid_hcv_addresses as (
    select kid_id, address_id, 
        greatest(min(date_admitted), min(k.date_of_birth)) as date
    from input.hcv
    join aux.kid_hcvs using (hcv_id)
    join aux.kids k using (kid_id)
    -- TODO: use actual geocoder
    join aux.addresses a on 
        regexp_replace(regexp_replace(upper(trim(hcv.address)), '[^A-Z0-9 ]', '', 'g'),
           'S KING DR', 'S DR MARTIN LUTHER KING JR DR') = a.address
    group by 1,2
);

drop table if exists discontinuity.addresses;

create table discontinuity.addresses as (
    select kid_id, address_id, 
        address_id = first_sample_address_id as first_sample_address
    from output.kids join discontinuity.max_bll_under1 using (kid_id) 
    join output.kid_addresses using (kid_id) 
    where address_min_date <= first_sample_date 
);

alter table discontinuity.addresses add primary key (kid_id, address_id);


drop table if exists aux.parcel_address;

create table aux.parcel_address as (
    select distinct on ("PIN") 
        "PIN", house_num, st_dir, st_name, st_suffix,
            substring(house_num from 6)::int || ' ' || coalesce(st_dir || ' ', '') ||
               case when st_name = 'SAINT LAWRENCE' then 'ST LAWRENCE'
                    when st_name = 'SAINT LOUIS' then 'ST LOUIS'
                    when st_name in ('MARTIN LUTHER KING', 'KING', 'SOUTH PARK') then 'DR MARTIN LUTHER KING JR'
                    when st_name = 'LASALLE' then 'LA SALLE'
                    else st_name end || 
                -- some sts don't have a suffice, like "AVENUE A"
                coalesce(' ' || 
                    case when st_suffix = 'PKY' then 'PKWY' 
                         when st_name = 'SOUTH PARK' then 'DR' 
                    end, '') as address
    from input.assessor
    where city = 'CHICAGO' and st_name is not null
    order by 1
);

alter table aux.parcel_address add primary key ("PIN");

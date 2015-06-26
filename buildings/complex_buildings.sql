drop table if exists buildings.complex_buildings;

create table buildings.complex_buildings as (

select b.id, cc.id1 as complex_id 
from buildings.buildings b join buildings.complex_components cc on cc.id2 = b.id
group by b.id, cc.id1
);


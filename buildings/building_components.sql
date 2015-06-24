DROP TABLE IF EXISTS buildings.building_components;
CREATE TABLE buildings.building_components (id1 int, id2 int);

\COPY buildings.building_components FROM data/building_components.csv WITH CSV

WITH singles as (
	select distinct orig_bldg_ id from buildings.original_buildings b
	left join buildings.building_components bc on b.orig_bldg_ = bc.id2
	where bc.id2 is null
)

INSERT INTO buildings.building_components
SELECT id,id from singles;

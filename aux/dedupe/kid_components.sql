DROP TABLE IF EXISTS aux.kid_components;
CREATE TABLE aux.kid_components (id1 int, id2 int);

\COPY aux.kid_components FROM data/kid_components.csv WITH CSV

WITH singles as (
	select id from aux.kids_initial ki
	left join aux.kid_components kc on ki.id = kc.id2
	where kc.id2 is null
)

INSERT INTO aux.kid_components
SELECT id,id from singles;
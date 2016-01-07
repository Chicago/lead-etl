with addresses_to_geocode as (
	select * from aux.geocode
	where rating is null order by in_address limit 100
)
update aux.geocode 
SET (address, number, predirAbbrev, streetName, streetTypeAbbrev, location, stateAbbrev, zip, geom, rating)=(
	pprint_addy((g.geo).addy),
	((g.geo).addy).address,
	((g.geo).addy).predirAbbrev,
	((g.geo).addy).streetName,
	((g.geo).addy).streetTypeAbbrev,
	((g.geo).addy).location,
	((g.geo).addy).stateAbbrev,
	((g.geo).addy).zip,
	(g.geo).geomout,
	COALESCE((g.geo).rating,-1)
)
FROM 
	(SELECT in_address
		from addresses_to_geocode) AS a
	left join (
		select in_address,
		-- geocode's internal regexp calls don't escape asterisks!
		geocode(regexp_replace(in_address, '\*', '-', 'g') || ', CHICAGO IL, ' || in_zip, 1) as geo
		from addresses_to_geocode
	) As g
	using(in_address)
WHERE a.in_address = geocode.in_address
;

-- todo don't bother geocoding addresses that are obviously bad! e.g. po boxes
-- truncate zip code to 5 chars
-- deal with 'AVE [A-Z]' geocoding! tiger stores them as '[A-Z] AVE'
-- decide whether geocode was accurate using rating or custom levenshtein
DROP TABLE IF EXISTS input.surnames;

CREATE TABLE input.surnames (
	surname text primary key,
	rank integer,
	count integer,
	prop100k decimal,
	cum_prop100k decimal,
	pct_white decimal,
	pct_black decimal,
	pct_api decimal,
	pct_aian decimal,
	pct_2prace decimal,
	pct_hispanic decimal
);

\COPY input.surnames FROM 'data/surnames/surnames.csv' WITH CSV HEADER;

ALTER TABLE input.surnames ADD COLUMN ethnicity text;
UPDATE input.surnames SET ethnicity =
CASE 
	WHEN pct_white >= greatest(pct_black, pct_api, pct_aian, pct_2prace, pct_hispanic, 0)
		THEN 'white'
	WHEN pct_black >= greatest(pct_api, pct_aian, pct_2prace, pct_hispanic, 0)
		THEN 'black'
	WHEN pct_api >= greatest(pct_aian, pct_2prace, pct_hispanic, 0)
		THEN 'api'
	WHEN pct_aian >= greatest(pct_2prace, pct_hispanic, 0) THEN 'aian'
	WHEN pct_2prace >= greatest(pct_hispanic,0) THEN '2prace'
	WHEN pct_hispanic is not null THEN 'hispanic'
	ELSE null
END;

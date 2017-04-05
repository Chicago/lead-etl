create table if not exists aux.geocode (
	in_address text primary key,
	in_zip text,
	address text,
	number int,
	predirAbbrev text,
	streetName text,
	streetTypeAbbrev text,
	location text,
	stateAbbrev text,
	zip text,
	geom geometry,
	rating int
);

insert into aux.geocode (in_address, in_zip) (
	with test_addresses as (
		select clean_address2 as address, max(zip) from aux.tests
		where clean_address2 is not null
		group by upper(clean_address2)
	)
	select address,zip from test_addresses t
	left join aux.addresses a using (address)
	where a.id is null
);
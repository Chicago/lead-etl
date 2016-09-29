-- geocode stellars

DROP TABLE IF EXISTS aux.stellar_addresses;

CREATE TABLE aux.stellar_addresses AS (
	SELECT addr_id, address_id, addrline2 as apt
	FROM stellar.addr join aux.addresses on upper(assemaddr) = address
);

alter table aux.stellar_addresses add primary key (addr_id);

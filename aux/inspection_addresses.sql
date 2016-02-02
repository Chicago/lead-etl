-- geocode inspections

DROP TABLE IF EXISTS aux.inspection_addresses;

CREATE TABLE aux.inspection_addresses (
        inspection_addr_id int,
        address_id int,
        method text
);

WITH inspection_addresses AS (
	SELECT addr_id, address
	FROM input.inspections
	GROUP BY addr_id, address
)
INSERT INTO aux.inspection_addresses (
        SELECT t.addr_id, a.address_id, 'equal'
        FROM inspection_addresses t join aux.addresses a
        ON t.address = a.address
);

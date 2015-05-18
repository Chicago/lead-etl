-- geocode tests

DROP TABLE IF EXISTS aux.test_addresses CASCADE;

CREATE TABLE aux.test_addresses (
        test_id int,
        address_id int,
        method text
);

INSERT INTO aux.test_addresses (
        SELECT t.id, a.id, 'address'
        FROM aux.tests t join aux.addresses a
        ON t.clean_address = a.address
);

CREATE OR REPLACE VIEW tests_missing_addresses AS (
	SELECT t.id, t.address, t.clean_address, t.clean_address2
    FROM aux.tests t LEFT OUTER JOIN aux.test_addresses g
    ON t.id = g.test_id WHERE g.test_id is null
    AND t.address is not null
);

INSERT INTO aux.test_addresses (
        SELECT t.id, a.id, 'clean'
        FROM tests_missing_addresses t join aux.addresses a
        ON t.clean_address = a.address
);

INSERT INTO aux.test_addresses (
        SELECT t.id, a.id, 'clean2'
        FROM tests_missing_addresses t join aux.addresses a
        ON t.clean_address2 = a.address
);


-- geocode tests

DROP TABLE IF EXISTS aux.test_addresses CASCADE;

CREATE TABLE aux.test_addresses (
        test_id int,
        address_id int,
        method text
);

INSERT INTO aux.test_addresses (
        SELECT test_id, address_id, 'geocode'
        FROM aux.tests t join aux.addresses a
        ON t.geocode_address = a.address
);

CREATE OR REPLACE VIEW tests_missing_addresses AS (
	SELECT test_id, clean_address, address
    FROM aux.tests t LEFT JOIN aux.test_addresses g USING (test_id)
    WHERE g.test_id is null
    AND t.clean_address is not null
);

INSERT INTO aux.test_addresses (
        SELECT test_id, address_id, 'clean'
        FROM tests_missing_addresses t join aux.addresses a
        ON t.clean_address = a.address
);

INSERT INTO aux.test_addresses (
        SELECT test_id, address_id, 'address'
        FROM tests_missing_addresses t join aux.addresses a
        ON t.address = a.address
);

INSERT INTO aux.test_addresses (
        SELECT test_id, address_id, 'regex'
        FROM tests_missing_addresses t join aux.addresses a
        ON a.address = 
            regexp_replace(regexp_replace(clean_address, '[^\w \*]','','g'),
                      '(([^ ]* ){3,}(AVE|BLVD|CT|DR|HWY|PKWY|PL|RD|ROW|SQ|ST|TER|WAY))( .*)$', '\1')
);


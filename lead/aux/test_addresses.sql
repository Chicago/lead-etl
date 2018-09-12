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
        ON t.clean_address = a.address
);

CREATE OR REPLACE VIEW tests_missing_addresses AS (
	SELECT test_id, clean_address, address, regexp_replace(t.address, '[^\w \*]','','g') as word_address
    FROM aux.tests t LEFT JOIN aux.test_addresses g USING (test_id)
    WHERE g.test_id is null
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
            regexp_replace(regexp_replace(t.address, '[^\w \*]','','g'),
                      '(([^ ]* ){3,}(AVE|BLVD|CT|DR|HWY|PKWY|PL|RD|ROW|SQ|ST|TER|WAY))( .*)$', '\1')
);

alter table aux.test_addresses add primary key (test_id);

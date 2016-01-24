DROP TABLE IF EXISTS aux.dedupe;

CREATE TABLE aux.dedupe ( cluster_id int, test_ids int[], cornerstone_ids text[],
    first_name text, last_name text, mi text, date_of_birth date, address text, count int
);

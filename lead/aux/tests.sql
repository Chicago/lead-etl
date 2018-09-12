DROP TABLE IF EXISTS aux.tests CASCADE;

CREATE TABLE aux.tests AS (
    select * from blls.tests
);

alter table aux.tests add primary key (test_id);

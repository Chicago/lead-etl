psql -v ON_ERROR_STOP=1 -c "
DROP TABLE IF EXISTS input.hcv;

CREATE TABLE input.hcv (
    property_id text, tenant_id text, owner_name text, status text, 
    address text, address2 text, city text, state text, zipcode text,
    phone text, member_number int,
    child_name text, date_of_birth date, age int, ssn text,
    date_admitted date, last_action char, date_effective date
);"

cat $INPUT1 | sed 's/NULL//g' | psql -v ON_ERROR_STOP=1 -c "\COPY input.hcv FROM STDIN WITH CSV HEADER"

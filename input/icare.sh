psql -v ON_ERROR_STOP=1 -c "
DROP TABLE IF EXISTS input.icare;

CREATE TABLE input.icare (
    first_name text, mi text, last_name text, date_of_birth date, 
    sex char, race text, 
    address text, address_2 text, city text, state text, zip text, county text
);"

psql -v ON_ERROR_STOP=1 -c "\COPY input.icare FROM $1 WITH CSV HEADER"

psql -v ON_ERROR_STOP=1 -c "ALTER TABLE input.icare add id serial primary key;"

DROP TABLE IF EXISTS input.labs;

CREATE TABLE input.labs (
    name text, idph_lab_id int,
    address text, address2 text, city text, state text, zip text,
    contact text, phone text, extension text, fax text,
    solar_lab_id text
);

\COPY input.labs FROM ${INPUT1} WITH CSV HEADER;

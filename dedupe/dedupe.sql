CREATE TABLE aux.dedupe AS (
    cluster_id int, 
    first_name text, mi text, last_name text, date_of_birth date, count int
);

\COPY aux.dedupe FROM STDIN with CSV HEADER;

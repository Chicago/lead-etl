-- this script writes a csv for manual deduplication entry
-- change the first column 'dupe' to 1 to indicate a match

\copy (with k1 as (
    select * from aux.kids_initial where random()*(select count(*) from aux.kids_initial) < 20
),
k2 as (
    select k1.id id1, k2.id id2,
    k1.first_name fname1, k2.first_name fname2,
    k1.last_name lname1, k2.last_name lname2,
    k1.date_of_birth as dob1, k2.date_of_birth as dob2,
    least(abs(k1.min_sample_date - k2.min_sample_date), abs(k1.min_sample_date - k2.max_sample_date), abs(k1.max_sample_date - k2.min_sample_date), abs(k1.max_sample_date - k2.max_sample_date)) as testd,
    k1.num_tests num_tests1, k2.num_tests num_tests2
    from k1
    join aux.kids_initial k2 on k1.initials = k2.initials
)

select 0 as dupe, *, levenshtein(fname1, fname2) fnamed,  levenshtein(lname1, lname2) lnamed, levenshtein(fname1 || lname1, fname2 || lname2) as named, levenshtein(dob1::text, dob2::text) as dobd from k2 where levenshtein_less_equal(fname1 || lname1, fname2 || lname2, 4) <= 4 order by id1, levenshtein(fname1 || lname1, fname2 || lname2) + levenshtein(dob1::text, dob2::text) asc

) to ~/dedupe.csv with csv header;

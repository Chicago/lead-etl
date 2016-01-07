This folder contains code for extracting and deduplicating kid entities from the test data.

The process begins in ../tests.sql which cleans up the names by removing non-alphabetic (spaces, hyphens, etc.) characters from first and last names. 

Then kids_initial.sql creates kids using an exact match on name and date of birth. And kid_tests_initial.sql creates the associated mapping between tests and kids_initial.

The main deduplication step is kid_edges.sql, which creates a table of edges between "initial kids" based on a criterion including id (so only one edge is created per pair), name initials, and levenshtein distance on name and date of birth. 
This calculation takes 30 minutes on our PostgreSQL server to dedupe all 1.2m records to 1m kids.
The levenshtein_less_equal() on PostgreSQL is very fast but it could be rewritten to run in parallel in python and (with enough cores) would be faster. Note the process is only parallelizable because of the equality condition on initials.

Next kid_components.py recursively crawls the graph to extract connected components.
This requires either recursion or looping so we do it in python and use the initials condition to parallelize.

Finally kids.sql extracts a unique kid for each connected component, and kid_tests.sql reduces the kid_tests_initial mapping to use this kid.

#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO: put these tables in a schema
# TODO: generate the last query from the first
"""
This is an example of working with very large data. There are about
700,000 unduplicated donors in this database of Illinois political
campaign contributions.

With such a large set of input data, we cannot store all the comparisons
we need to make in memory. Instead, we will read the pairs on demand
from the PostgresSQL database.

__Note:__ You will need to run `python pgsql_big_dedupe_example_init_db.py`
before running this script.

For smaller datasets (<10,000), see our
[csv_example](http://datamade.github.io/dedupe-examples/docs/csv_example.html)
"""
import os
import csv
import tempfile
import time
import logging
import optparse
import locale

import psycopg2
import psycopg2.extras

import dedupe

source_table='dedupe.infants'
id_column = 'id'

import random
import numpy.random
random.seed(0)
numpy.random.seed(0)

# ## Logging

# Dedupe uses Python logging to show or suppress verbose output. Added
# for convenience.  To enable verbose output, run `python
# pgsql_big_dedupe_example.py -v`
optp = optparse.OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)'
                )
(opts, args) = optp.parse_args()
log_level = logging.WARNING
if opts.verbose == 1:
    log_level = logging.INFO
elif opts.verbose >= 2:
    log_level = logging.DEBUG
logging.getLogger().setLevel(log_level)

# ## Setup
#settings_file = 'asdf123445'
training_file = '/home/epotash/lead/data/dedupe/training_new.json'

start_time = time.time()

# Set the database connection from environment variable using
# [dj_database_url](https://github.com/kennethreitz/dj-database-url)
# For example:
#   export DATABASE_URL=postgres://user:password@host/mydatabase

#if not db_conf:
#    raise Exception(
#        'set DATABASE_URL environment variable with your connection, e.g. '
#        'export DATABASE_URL=postgres://user:password@host/mydatabase'
#    )

con = psycopg2.connect(database=os.environ['PGDATABASE'],
                       user=os.environ['PGUSER'],
                       password=os.environ['PGPASSWORD'],
                       host=os.environ['PGHOST'],
                       cursor_factory=psycopg2.extras.RealDictCursor)

c = con.cursor()

# We'll be using variations on this following select statement to pull
# in campaign donor info.
#
# We did a fair amount of preprocessing of the fields in
# `pgsql_big_dedupe_example_init_db.py`

DONOR_SELECT = "SELECT id, first_name, last_name, sex, day, date_of_birth, address, count " \
               "from %s" %  source_table

# ## Training

#if os.path.exists(settings_file):
#    print 'reading from ', settings_file
#    with open(settings_file) as sf:
#        deduper = dedupe.StaticDedupe(sf, num_cores=12)
#else:
if True:
    # Define the fields dedupe will pay attention to
    #
    # The address, city, and zip fields are often missing, so we'll
    # tell dedupe that, and we'll learn a model that take that into
    # account
    fields = [
            {"field" : "first_name", "type" : "String"},
            {"field" : "last_name", "type" : "String"},
            {"field" : "date_of_birth", "type" : "String"},
            {"field" : "address", "type" : "String"},
            {"field" : "sex", "type" : "Exact"},
            {"field" : "count", "type" : "Price"}
    ]

    # Create a new deduper object and pass our data model to it.
    deduper = dedupe.Dedupe(fields, num_cores=12)

    # Named cursor runs server side with psycopg2
    cur = con.cursor('donor_select')

    cur.execute(DONOR_SELECT)
    temp_d = dict((i, row) for i, row in enumerate(cur))

    deduper.sample(temp_d, 100000)
    del temp_d

    # If we have training data saved from a previous run of dedupe,
    # look for it an load it in.
    #
    # __Note:__ if you want to train from
    # scratch, delete the training_file
    print training_file
    if os.path.exists(training_file):
        print 'reading labeled examples from ', training_file
        with open(training_file) as tf:
            deduper.readTraining(tf)

    # ## Active learning

    print 'starting active labeling...'
    # Starts the training loop. Dedupe will find the next pair of records
    # it is least certain about and ask you to label them as duplicates
    # or not.

    # use 'y', 'n' and 'u' keys to flag duplicates
    # press 'f' when you are finished
    #dedupe.convenience.consoleLabel(deduper)

    # Notice our two arguments here
    #
    # `ppc` limits the Proportion of Pairs Covered that we allow a
    # predicate to cover. If a predicate puts together a fraction of
    # possible pairs greater than the ppc, that predicate will be removed
    # from consideration. As the size of the data increases, the user
    # will generally want to reduce ppc.
    #
    # `uncovered_dupes` is the number of true dupes pairs in our training
    # data that we are willing to accept will never be put into any
    # block. If true duplicates are never in the same block, we will never
    # compare them, and may never declare them to be duplicates.
    #
    # However, requiring that we cover every single true dupe pair may
    # mean that we have to use blocks that put together many, many
    # distinct pairs that we'll have to expensively, compare as well.
    deduper.train(maximum_comparisons=5000000000, recall=0.95)

    # When finished, save our labeled, training pairs to disk
    #with open(training_file, 'w') as tf:
    #    deduper.writeTraining(tf)
    #with open(settings_file, 'w') as sf:
    #    deduper.writeSettings(sf)

    # We can now remove some of the memory hobbing objects we used
    # for training
    deduper.cleanupTraining()

## Blocking
print 'blocking...'

# To run blocking on such a large set of data, we create a separate table
# that contains blocking keys and record ids
print 'creating blocking_map database'
c.execute("DROP TABLE IF EXISTS blocking_map")
c.execute("CREATE TABLE blocking_map "
          "(block_key VARCHAR(200), %s INTEGER)" % id_column)


# If dedupe learned a Index Predicate, we have to take a pass
# through the data and create indices.
print 'creating inverted index'

for field in deduper.blocker.index_fields:
    c2 = con.cursor('c2')
    c2.execute("SELECT DISTINCT %s FROM %s" % (field, source_table))
    field_data = (row[field] for row in c2)
    deduper.blocker.index(field_data, field)
    c2.close()

# Now we are ready to write our blocking map table by creating a
# generator that yields unique `(block_key, donor_id)` tuples.
print 'writing blocking map'

c3 = con.cursor('donor_select2')
c3.execute(DONOR_SELECT)
full_data = ((row[id_column], row) for row in c3)
b_data = deduper.blocker(full_data)

# Write out blocking map to CSV so we can quickly load in with
# Postgres COPY
csv_file = tempfile.NamedTemporaryFile(prefix='blocks_', delete=False)
csv_writer = csv.writer(csv_file)
csv_writer.writerows(b_data)
c3.close()
csv_file.close()

f = open(csv_file.name, 'r')
c.copy_expert("COPY blocking_map FROM STDIN CSV", f)
f.close()

os.remove(csv_file.name)

con.commit()


# Remove blocks that contain only one record, sort by block key and
# donor, key and index blocking map.
#
# These steps, particularly the sorting will let us quickly create
# blocks of data for comparison
print 'prepare blocking table. this will probably take a while ...'

logging.info("indexing block_key")
c.execute("CREATE INDEX blocking_map_key_idx ON blocking_map (block_key)")

c.execute("DROP TABLE IF EXISTS plural_key")
c.execute("DROP TABLE IF EXISTS plural_block")
c.execute("DROP TABLE IF EXISTS covered_blocks")
c.execute("DROP TABLE IF EXISTS smaller_coverage")

# Many block_keys will only form blocks that contain a single
# record. Since there are no comparisons possible withing such a
# singleton block we can ignore them.
logging.info("calculating plural_key")
c.execute("CREATE TABLE plural_key "
          "(block_key VARCHAR(200), "
          " block_id SERIAL PRIMARY KEY)")

c.execute("INSERT INTO plural_key (block_key) "
          "SELECT block_key FROM blocking_map "
          "GROUP BY block_key HAVING COUNT(*) > 1")

logging.info("creating block_key index")
c.execute("CREATE UNIQUE INDEX block_key_idx ON plural_key (block_key)")

logging.info("calculating plural_block")
c.execute("CREATE TABLE plural_block "
          "AS (SELECT block_id, %s "
          " FROM blocking_map INNER JOIN plural_key "
          " USING (block_key))" % id_column)

logging.info("adding %s index and sorting index" % id_column)
c.execute("CREATE INDEX plural_block_%s_idx ON plural_block (%s)" % (id_column, id_column))
c.execute("CREATE UNIQUE INDEX plural_block_block_id_%s_uniq "
          " ON plural_block (block_id, %s)" % (id_column, id_column))


# To use Kolb, et.al's Redundant Free Comparison scheme, we need to
# keep track of all the block_ids that are associated with a
# particular donor records. We'll use PostgreSQL's string_agg function to
# do this. This function will truncate very long lists of associated
# ids, so we'll also increase the maximum string length to try to
# avoid this.
# c.execute("SET group_concat_max_len = 2048")

logging.info("creating covered_blocks")
c.execute("CREATE TABLE covered_blocks "
          "AS (SELECT %s, "
          " string_agg(CAST(block_id AS TEXT), ',' ORDER BY block_id) "
          "   AS sorted_ids "
          " FROM plural_block "
          " GROUP BY %s)" % (id_column, id_column))

c.execute("CREATE UNIQUE INDEX covered_blocks_%s_idx "
          "ON covered_blocks (%s)" % (id_column, id_column))

con.commit()

# In particular, for every block of records, we need to keep
# track of a donor records's associated block_ids that are SMALLER than
# the current block's id. Because we ordered the ids when we did the
# GROUP_CONCAT we can achieve this by using some string hacks.
logging.info("creating smaller_coverage")
c.execute("CREATE TABLE smaller_coverage "
          "AS (SELECT %s, block_id, "
          " TRIM(',' FROM split_part(sorted_ids, CAST(block_id AS TEXT), 1)) "
          "      AS smaller_ids "
          " FROM plural_block INNER JOIN covered_blocks "
          " USING (%s))" % (id_column, id_column))

con.commit()


## Clustering

def candidates_gen(result_set):
    lset = set

    block_id = None
    records = []
    i = 0
    for row in result_set:
        if row['block_id'] != block_id:
            if records:
                yield records

            block_id = row['block_id']
            records = []
            i += 1

            if i % 10000 == 0:
                print i, "blocks"
                print time.time() - start_time, "seconds"

        smaller_ids = row['smaller_ids']

        if smaller_ids:
            smaller_ids = lset(smaller_ids.split(','))
        else:
            smaller_ids = lset([])

        records.append((row[id_column], row, smaller_ids))

    if records:
        yield records

c4 = con.cursor('c4')
c4.execute("SELECT %s, first_name, last_name, sex, day, date_of_birth, address, count, "
           "block_id, smaller_ids "
           "FROM smaller_coverage "
           "INNER JOIN %s "
           "USING (%s) "
           "ORDER BY (block_id)" % (id_column, source_table, id_column))

print 'clustering...'
clustered_dupes = deduper.matchBlocks(candidates_gen(c4),
                                      threshold=0.5)

## Writing out results

# We now have a sequence of tuples of donor ids that dedupe believes
# all refer to the same entity. We write this out onto an entity map
# table
c.execute("DROP TABLE IF EXISTS entity_map")

print 'creating entity_map database'
c.execute("CREATE TABLE entity_map "
          "(%s INTEGER, canon_id INTEGER, "
          " cluster_score FLOAT, PRIMARY KEY(%s))" % (id_column, id_column))

csv_file = tempfile.NamedTemporaryFile(prefix='entity_map_', delete=False)
csv_writer = csv.writer(csv_file)


for cluster, scores in clustered_dupes:
    cluster_id = cluster[0]
    for donor_id, score in zip(cluster, scores) :
        csv_writer.writerow([donor_id, cluster_id, score])

c4.close()
csv_file.close()

f = open(csv_file.name, 'r')
c.copy_expert("COPY entity_map FROM STDIN CSV", f)
f.close()

os.remove(csv_file.name)

con.commit()

c.execute("CREATE INDEX head_index ON entity_map (canon_id)")
con.commit()

# Print out the number of duplicates found
print '# duplicate sets'
print len(clustered_dupes)

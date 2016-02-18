#! /usr/bin/python
from drain import util
import pandas as pd

engine = util.create_engine()
acs = pd.read_sql("select * from input.acs "
        "where length(census_tract_id::text) = 11", engine, 
        index_col=['census_tract_id', 'year'])

props = pd.DataFrame()
categories = ['tenure', 'health', 'edu', 'race']

# get all columns
columns = {cat: [c for c in acs.columns 
        if c.startswith(cat) and not c.endswith('total')] 
            for cat in categories}

for category in categories:
    for c in columns[category]:
        props[c.replace('_count_', '_prop_')] = \
            acs[c] / acs[category + '_count_total']

props.to_sql(name='acs', schema='output', con=engine, 
        if_exists='replace', index=True)

import sys
import pandas as pd
import numpy as np
from lead.aux.dedupe import dedupe
from sqlalchemy.types import Integer, Text
from drain import util

# given a dataframe with index and column which is a string rep of a psql array
# unnest the array
def unnest(df):
    index, column = df.columns
    df[column] = df[column].apply(lambda d: d[1:-1].split(','))
    array = np.concatenate([np.array([[i]*len(values), values]).T for i, values in df.values])

    return pd.DataFrame(array)

output = pd.read_csv(sys.argv[1])

# find sets of exact matches which didn't get clustered
grouped = output.fillna(-1).groupby(['first_name', 'last_name', 'date_of_birth'])
duped = grouped['Cluster ID'].agg(lambda l: set(l))
multiple = duped.apply(lambda a: len(a) > 1)

# turn them into edges by linking all of them to one of them
groups = duped[multiple].values
edges = []
for group in groups:
    id = group.pop()
    for i in group:
       edges.append([id, i])

# crawl the graph for components in case multple clusters got linked
edges = pd.DataFrame(edges, columns=['id1','id2'])
components = dedupe.get_components(edges)

# merge the clusters into one of them
for id, component in components.iteritems():
    for i in component:
        output['Cluster ID'].replace(i, id, inplace=True)


test_ids = unnest(output[['Cluster ID', 'test_ids']].dropna())
test_ids.columns = ['kid_id', 'test_id']

cornerstone_ids = unnest(output[['Cluster ID', 'cornerstone_ids']].dropna())
cornerstone_ids.columns = ['kid_id', 'part_id_i']

# write the result
engine = util.create_db()
db.to_sql(frame=test_ids, if_exists='replace', name='kid_tests', schema='aux', dtype={'kid_id': Integer, 'test_id':Integer}, index=False)
db.to_sql(frame=test_ids, if_exists='replace', name='kid_wics', schema='aux', dtype={'kid_id':Integer, 'part_id_i':Text}, index=False)

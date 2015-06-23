import pandas as pd
import numpy as np
from lead.model import util
import sys
import dedupe

engine = util.create_engine()
vertices = pd.read_sql("select id1 as id from aux.kid_edges where initials='{initials}' UNION select id2 from aux.kid_edges where initials='{initials}';".format(initials=sys.argv[1]), engine)
edges = pd.read_sql("select * from aux.kid_edges where initials = '{}'".format(sys.argv[1]), engine)

components = dedupe.get_components(vertices, edges)
deduped = np.empty((0,2), dtype=int)

for id1 in components:
    deduped = np.append(deduped, [[id1, id2] for id2 in components[id1]], axis=0)

deduped = pd.DataFrame(deduped, columns=['id1', 'id2'])
if len(deduped) > 0:
    print deduped.to_csv(index=False, header=False),

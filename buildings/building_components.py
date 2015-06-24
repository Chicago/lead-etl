#! /usr/bin/python

import pandas as pd
import numpy as np
from lead.model import util
from lead.aux.dedupe import dedupe

engine = util.create_engine()
edges = pd.read_sql("with addresses as (select a.id, oa.orig_bldg_ from buildings.addresses a join buildings.original_addresses oa using (address)) select a1.orig_bldg_ id1, a2.orig_bldg_ id2 from addresses a1 join addresses a2 using (id) where a1.orig_bldg_ < a2.orig_bldg_;", engine)
vertices = pd.DataFrame({'id':pd.concat((edges['id1'], edges['id2'])).unique()})

components = dedupe.get_components(vertices, edges)
deduped = np.empty((0,2), dtype=int)

for id1 in components:
    deduped = np.append(deduped, [[id1, id2] for id2 in components[id1]], axis=0)

deduped = pd.DataFrame(deduped, columns=['id1', 'id2'])
print deduped.to_csv(index=False, header=False),

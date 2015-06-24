import pandas as pd
import numpy as np
from lead.model import util
from lead.aux.dedupe import dedupe

engine = util.create_engine()
vertices = pd.read_sql('select distinct orig_bldg_ as id from input.buildings', engine)
edges = pd.read_sql("select b1.orig_bldg_ id1, b2.orig_bldg_ id2 from input.buildings b1 join input.buildings b2 using (f_add1, t_add1,pre_dir1, st_name1, st_type1) where b1.orig_bldg_ < b2.orig_bldg_", engine)

components = dedupe.get_components(vertices, edges, sparse=True)
deduped = np.empty((0,2), dtype=int)

for id1 in components:
    deduped = np.append(deduped, [[id1, id2] for id2 in components[id1]], axis=0)

deduped = pd.DataFrame(deduped, columns=['id1', 'id2'])
deduped.to_sql('buildings', engine, schema='buildings', if_exists='replace', index=False)
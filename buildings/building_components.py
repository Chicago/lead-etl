#! /usr/bin/python

import pandas as pd
import numpy as np
from lead.model import util
from lead.aux.dedupe import dedupe

engine = util.create_engine()
edges = pd.read_sql("with addresses as (select a.id, oa.orig_bldg_ from buildings.addresses a join buildings.original_addresses oa using (address)) select a1.orig_bldg_ id1, a2.orig_bldg_ id2 from addresses a1 join addresses a2 using (id) where a1.orig_bldg_ < a2.orig_bldg_;", engine)

components = dedupe.get_components(edges)
deduped = dedupe.components_dict_to_df(components)

print deduped.to_csv(index=False, header=False),

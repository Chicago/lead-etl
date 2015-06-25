import pandas as pd
import numpy as np
from lead.model import util
import sys
import dedupe

engine = util.create_engine()
edges = pd.read_sql("select * from aux.kid_edges where initials = '{}'".format(sys.argv[1]), engine)

components = dedupe.get_components(edges)
deduped = dedupe.components_dict_to_df(components)

if len(deduped) > 0:
    print deduped.to_csv(index=False, header=False),

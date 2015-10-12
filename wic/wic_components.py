import pandas as pd
import numpy as np
from drain import util
from drain.util import PgSQLDatabase
import sys
from lead.aux.dedupe import dedupe

engine = util.create_engine()
db = PgSQLDatabase(engine)

edges = pd.read_sql("select * from wic.wic_edges", engine)
c = dedupe.get_components(edges)
components = dedupe.components_dict_to_df(c)

db.to_sql(frame=components, name='wic_components', schema='wic', index=False, if_exists='replace')        

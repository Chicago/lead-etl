#!/usr/bin/python
import pandas as pd
import sys
from lead.model import util

engine = util.create_engine()
db = util.PgSQLDatabase(engine)

df = pd.read_csv(sys.argv[1], dtype={'addr_zi':float, 'hseh':float, 'hse_inc_':float})
db.to_sql(df, 'wic', if_exists='append', schema='input', index=False)

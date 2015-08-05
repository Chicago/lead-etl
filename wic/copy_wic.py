#!/usr/bin/python
import pandas as pd
import sys
from lead.model import util

tablename = 'wic_' + ('pregnant' if sys.argv[1].endswith('_P.csv') else 'infant')

engine = util.create_engine()
db = util.PgSQLDatabase(engine)

dtype = {'addr_zi':float, 'hseh':float, 'hse_inc_':float, 'pa_c':float}
for i in xrange(4):
    dtype['pa_c.'+str(i)] = float

df = pd.read_csv(sys.argv[1], dtype=dtype)
db.to_sql(df, tablename, if_exists='append', schema='input', index=False)

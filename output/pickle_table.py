#!/usr/bin/python
import pandas as pd
from lead.model import util
import sys

engine = util.create_engine()
df = pd.read_sql('select * from {table_name}'.format(table_name=sys.argv[1]), engine)
df.to_pickle(sys.argv[2])

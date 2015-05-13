#! /usr/bin/python
import pandas as pd
from lead.model import util
import sys

acs = pd.read_csv(sys.argv[1])
engine = util.create_engine()
acs.to_sql(name='acs', con=engine, schema='input', if_exists='replace', index=False)


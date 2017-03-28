import pandas as pd
from drain import util
import sys

acs = pd.read_csv(sys.argv[1], dtype= {'census_tract_id':float})
db = util.create_db()
db.to_sql(acs, name='acs', con=engine, schema='input', if_exists='replace', index=False)

import pandas as pd
from drain import util
import sys

df = pd.read_csv(sys.argv[1]).append(pd.read_csv(sys.argv[2]))
df['address'] = df.HOUSE_HIGH + ' ' + df.PRE + ' ' + df.STREET_NAME + ' ' + df.STREET_TYPE
df2 = df[df.STATUS1=='VALID'][['addr_ln1_t', 'addr_zi', 'address', 'XCOORD', 'YCOORD']].drop_duplicates()

df2.XCOORD = df2.XCOORD.astype(float)
df2.YCOORD = df2.YCOORD.astype(float)

db = util.create_db()
db.to_sql(frame=df2, name='wic_addresses', schema='input', index=False, if_exists='replace')

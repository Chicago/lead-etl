#!/usr/bin/python
from drain import util
import pandas as pd
from drain import data

engine = util.create_engine()

# read tables from db
building_permits = pd.read_sql("select street_number || ' ' || street_direction || ' ' || street_name || ' ' || suffix as address, issue_date, lower(replace(substring(permit_type from 10), '/', ' ')) as permit_type from input.building_permits where issue_date is not null", engine)

data.binarize(building_permits, {'permit_type' : building_permits.permit_type.unique()}, all_classes=True)

db = util.PgSQLDatabase(engine)
db.to_sql(frame=building_permits, name='building_permits',if_exists='replace', index=False, schema='aux')

#!/usr/bin/python
from lead.model import util
import pandas as pd
import numpy as np
from lead.output.aggregate import aggregate
from lead.model.data import prefix_columns
from lead.model.util import PgSQLDatabase
import sys

columns = {
    'building_count': {'numerator':1},
    'area_sum': {'numerator': 'area'},
    'year' : {'numerator':'year_built', 'func':np.mean},
    'year_min' : {'numerator':'year_built', 'func':np.min},
    'year_max' : {'numerator':'year_built', 'func':np.max},
    'address_count' : {'numerator' : 'address_count'},
    'condition_sound_prop': {'numerator': 'condition_sound_prop', 'denominator':'condition_not_null'},
    'condition_major_prop': {'numerator': 'condition_major_prop', 'denominator':'condition_not_null'},
    'condition_minor_prop': {'numerator': 'condition_minor_prop', 'denominator':'condition_not_null'},
    'condition_uninhabitable_prop': {'numerator': 'condition_uninhabitable_prop', 'denominator':'condition_not_null'},
    'stories_avg' : {'numerator':'stories', 'func':np.mean},
    'units_avg' : {'numerator':'units'},
    'pre_1978_prop' : {'numerator': 'pre_1978', 'denominator': lambda b: b.pre_1978.notnull()},
}

engine = util.create_engine()

buildings = pd.read_sql('select * from aux.buildings', engine)
complex_buildings = pd.read_sql('select * from buildings.complex_buildings', engine)

# complex-level aggregation
df = complex_buildings.merge(buildings, on='building_id')
buildings_ag = aggregate(df, columns, index='complex_id')

# aggregate assessor to complex
assessor = pd.read_sql("select * from aux.assessor_summary", engine)
addresses = pd.read_sql("select id, address, census_tract_id, ward_id from aux.addresses", engine)
complex_addresses = pd.read_sql("select * from aux.complex_addresses", engine)
df0 = assessor.merge(addresses, on='address').merge(complex_addresses, left_on='id', right_on='address_id')

assessor_columns = {
    'count' : {'numerator' : 'count', 'func': np.mean},
    'land_value' : {'numerator': 'land_value'},
    'improved_value' : {'numerator': 'improved_value'},
    'total_value': {'numerator': 'total_value'},
    'age_min':{'numerator': 'age', 'func': np.min},
    'age':{'numerator': 'age', 'func': np.mean},
    'age_max':{'numerator': 'age', 'func': np.max},
    'apartments':{'numerator':'apartments'},
    'rooms':{'numerator':'rooms'},
    'beds':{'numerator':'beds'},
    'baths':{'numerator':'baths'},
    'building_area':{'numerator':'building_area'},
    'land_area':{'numerator':'land_area'},
    'residential':{'numerator':'residential', 'denominator':1}
}

assessor_ag = aggregate(df0, assessor_columns, index='complex_id')

buildings_ag['null'] = False
assessor_ag['null'] = False

prefix_columns(buildings_ag, 'building_')
prefix_columns(assessor_ag, 'assessor_')

complexes = buildings_ag.join(assessor_ag, how='outer')
complexes['building_null'].fillna(True, inplace=True)
complexes['assessor_null'].fillna(True, inplace=True)

prefix_columns(complexes, 'complex_')

db = PgSQLDatabase(engine)
db.to_sql(frame=complexes,name='complexes',if_exists='replace', index=True, schema='output')

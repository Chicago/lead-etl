#!/usr/bin/python
from lead.model import util
import pandas as pd
import numpy as np
from lead.output.aggregate import aggregate
from lead.model.data import prefix_columns
from lead.model.util import PgSQLDatabase
import sys

building_columns = {
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


engine = util.create_engine()
util.execute_sql(engine, 'DROP TABLE IF EXISTS output.buildings_aggregated')
db = PgSQLDatabase(engine)

buildings = pd.read_sql('select b.*, a.* from aux.buildings b join aux.complex_addresses ca using (building_id) join output.addresses a using(address_id)', engine)
assessor = pd.read_sql("select * from aux.assessor_summary ass join output.addresses using (address)", engine)

levels = ['complex_id', 'census_block_id', 'census_tract_id', 'ward_id', 'community_area_id']

for level in levels:
    print level
    # use double because a) tract and block are too big for int and b) pandas missing ints suck
    buildings[level] = buildings[level].astype(np.float64)
    assessor[level] = assessor[level].astype(np.float64)

    buildings_subset = buildings[buildings[level].notnull()]
    assessor_subset = assessor[assessor[level].notnull()]

    buildings_ag = aggregate(buildings_subset, building_columns, index=level)
    assessor_ag = aggregate(assessor_subset, assessor_columns, index=level)
    
    buildings_ag['null'] = False
    assessor_ag['null'] = False
    
    prefix_columns(buildings_ag, 'building_')
    prefix_columns(assessor_ag, 'assessor_')
    
    df = buildings_ag.join(assessor_ag, how='outer')
    df['aggregation_level'] = level
    df.reset_index(inplace=True)
    df.rename(columns={level:'aggregation_id'}, inplace=True)

    df['building_null'].fillna(True, inplace=True)
    df['assessor_null'].fillna(True, inplace=True)
    
    db.to_sql(frame=df,name='buildings_aggregated',if_exists='append', index=False, schema='output')

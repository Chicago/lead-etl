#!/usr/bin/python
from lead.model import util
import pandas as pd
import numpy as np
from lead.output.aggregate import aggregate
from lead.model.data import prefix_columns
from lead.model.util import PgSQLDatabase
import sys

columns0 = {
    'area': {'numerator': 'area', 'func':np.mean},
    'year_built' : {'numerator':'year_built', 'func':np.mean},
    'address_count' : {'numerator' : lambda b: (b.t_add1 - b.f_add1)/2+1, 'func':np.max},
    'condition_not_null' : {'numerator' : 'bldg_condi_not_null', 'func':np.any},
    'condition_sound_prop': {'numerator':lambda b: b.bldg_condi == 'SOUND', 'denominator':'bldg_condi_not_null'},
    'condition_major_prop': {'numerator':lambda b: b.bldg_condi == 'NEEDS MAJOR REPAIR', 'denominator':'bldg_condi_not_null'},
    'condition_minor_prop': {'numerator':lambda b: b.bldg_condi == 'NEEDS MINOR REPAIR', 'denominator':'bldg_condi_not_null'},
    'condition_uninhabitable_prop': {'numerator':lambda b: b.bldg_condi == 'UNINHABITABLE', 'denominator':'bldg_condi_not_null'},
    'stories' : {'numerator':'stories', 'func':np.mean},
    'units' : {'numerator':'no_of_unit', 'func': np.mean},
    'pre_1978' : {'numerator' : lambda b: b.year_built < 1978, 'func':np.any}
}

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

# read tables from db
building_components = pd.read_sql('select * from buildings.building_components', engine)

buildings = pd.read_sql("""select ogc_fid id,
t_add1, f_add1, bldg_condi, vacancy_st is not null as vacant, nullif(stories,0) as stories,
nullif(no_of_unit,0) as no_of_unit, nullif(year_built, 0) as year_built,
st_area(wkb_geometry) as area from input.buildings"""
, engine)

complex_buildings = pd.read_sql('select * from buildings.complex_buildings', engine)

# initial building-level aggregation
df0 = building_components.merge(buildings, left_on='id2', right_on='id')
df0['bldg_condi_not_null'] = df0['bldg_condi'].notnull()
buildings_ag = aggregate(df0, columns0, index='id1')
buildings_ag.reset_index(inplace=True)

# complex-level aggregation
df = complex_buildings.merge(buildings_ag, left_on='building_id', right_on='id1')
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

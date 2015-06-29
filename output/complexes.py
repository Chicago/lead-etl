#!/usr/bin/python
from lead.model import util
import pandas as pd
import numpy as np
from lead.output.aggregate import aggregate

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
    'year_built_avg' : {'numerator':'year_built', 'func':np.mean},
    'year_built_min' : {'numerator':'year_built', 'func':np.min},
    'year_built_max' : {'numerator':'year_built', 'func':np.max},
    'address_count' : {'numerator' : 'address_count'},
    'condition_sound_prop': {'numerator': 'condition_sound_prop', 'denominator':'condition_not_null'},
    'condition_major_prop': {'numerator': 'condition_major_prop', 'denominator':'condition_not_null'},
    'condition_minor_prop': {'numerator': 'condition_minor_prop', 'denominator':'condition_not_null'},
    'condition_uninhabitable_prop': {'numerator': 'condition_uninhabitable_prop', 'denominator':'condition_not_null'},
    'stories_avg' : {'numerator':'stories', 'func':np.mean},
    'units_avg' : {'numerator':'units'},
    'pre_1978_prop' : {'numerator': 'pre_1978', 'denominator': lambda b: b.pre_1978.isnull()},
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
complex_ag = aggregate(df, columns, index='complex_id')
complex_ag.to_sql('complexes', engine, schema='output', if_exists='replace', index=True)

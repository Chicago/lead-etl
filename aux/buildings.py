#!/usr/bin/python
from drain import util
import pandas as pd
import numpy as np
from drain.aggregate import aggregate
from drain.util import PgSQLDatabase, prefix_columns
from sqlalchemy.dialects.postgresql import ARRAY
from  sqlalchemy.types import Float
import sys

columns0 = {
    'area': {'numerator': 'area', 'func': 'mean'},
    'years_built' : {'numerator':'year_built', 'func': lambda l: list(l)},
    'address_count' : {'numerator' : lambda b: (b.t_add1 - b.f_add1)/2+1, 'func': 'max'},
    'condition_not_null' : {'numerator' : 'bldg_condi_not_null', 'func':np.any},
    'condition_sound_prop': {'numerator':lambda b: b.bldg_condi == 'SOUND', 'denominator':'bldg_condi_not_null'},
    'condition_major_prop': {'numerator':lambda b: b.bldg_condi == 'NEEDS MAJOR REPAIR', 'denominator':'bldg_condi_not_null'},
    'condition_minor_prop': {'numerator':lambda b: b.bldg_condi == 'NEEDS MINOR REPAIR', 'denominator':'bldg_condi_not_null'},
    'condition_uninhabitable_prop': {'numerator':lambda b: b.bldg_condi == 'UNINHABITABLE', 'denominator':'bldg_condi_not_null'},
    'stories' : {'numerator':'stories', 'func': 'mean'},
    'units' : {'numerator':'no_of_unit', 'func': 'mean'},
    'pre_1978' : {'numerator' : lambda b: b.year_built < 1978, 'func':np.any}
}

engine = util.create_engine()

# read tables from db
building_components = pd.read_sql('select * from buildings.building_components', engine)

buildings = pd.read_sql("""select ogc_fid id,
t_add1, f_add1, bldg_condi, vacancy_st is not null as vacant, nullif(stories,0) as stories,
nullif(no_of_unit,0) as no_of_unit, nullif(year_built, 0) as year_built,
st_area(wkb_geometry) as area from input.buildings"""
, engine)

# initial building-level aggregation
df0 = building_components.merge(buildings, left_on='id2', right_on='id')
df0['bldg_condi_not_null'] = df0['bldg_condi'].notnull()
buildings_ag = aggregate(df0, columns0, index='id1')
buildings_ag.reset_index(inplace=True)
buildings_ag.rename(columns={'id1':'building_id'}, inplace=True)

# convert int[] to postgresql string rep so it works with \copy
buildings_ag['years_built'] = buildings_ag['years_built'].apply(lambda a: '{' + str.join(',', map(str, a)) + '}')

db = PgSQLDatabase(engine)
db.to_sql(frame=buildings_ag, name='buildings',if_exists='replace', index=False, schema='aux', dtype={'years_built':ARRAY(Float)})

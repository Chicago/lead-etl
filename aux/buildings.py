import sys
import pandas as pd
import numpy as np

from drain import util, data
from drain.aggregate import Count, Aggregate, Aggregator, Fraction
from drain.util import PgSQLDatabase

from sqlalchemy.dialects.postgresql import ARRAY
from  sqlalchemy.types import Float

conditions = ('SOUND', 'NEEDS MAJOR REPAIR', 'NEEDS MINOR REPAIR', 'UNINHABITABLE')
cond = Aggregate([(lambda b,c=c: b.bldg_condi == c) for c in conditions], 
        'sum', name=['condition_sound', 'condition_major', 
                     'condition_minor', 'condition_uninhabitable'], fname=False)

aggregates = [
    Aggregate('area', 'mean', fname=False),
    Aggregate('year_built', lambda l: list(l), 
            name='years_built', fname=False),
    Aggregate(lambda b: (b.t_add1 - b.f_add1)/2+1, 'max',
            name='address_count', fname=False),
    Aggregate('bldg_condi_not_null', 'any', 
            name='condition_not_null', fname=False),
    Aggregate('stories', 'mean', fname=False),
    Aggregate('units', 'mean', fname=False),
    Fraction(Count(lambda b: b.year_built < 1978),
             Count(lambda b: b.year_built.notnull()),
             name='pre1978_prop'),
    Fraction(cond, Count(lambda  b: b.bldg_condi.notnull()),
            name='{numerator}_prop')
]

engine = util.create_engine()
# read tables from db
building_components = pd.read_sql('select * from buildings.building_components', engine)

buildings = pd.read_sql("""
select ogc_fid id,
    t_add1, f_add1, bldg_condi, vacancy_st is not null as vacant, nullif(stories,0) as stories,
    nullif(no_of_unit,0) as units, nullif(year_built, 0) as year_built,
    st_area(wkb_geometry) as area 
from input.buildings"""
, engine)

# initial building-level aggregation
df0 = building_components.merge(buildings, left_on='id2', right_on='id')
df0['bldg_condi_not_null'] = df0['bldg_condi'].notnull()

aggregator = Aggregator(df0, aggregates)
buildings_ag = aggregator.aggregate('id1')

buildings_ag.reset_index(inplace=True)
buildings_ag.rename(columns={'id1':'building_id'}, inplace=True)

# convert int[] to postgresql string rep so it works with \copy
buildings_ag['years_built'] = buildings_ag['years_built'].apply(lambda a: '{' + str.join(',', map(str, a)) + '}')

db = PgSQLDatabase(engine)
db.to_sql(frame=buildings_ag, name='buildings',if_exists='replace', index=False, schema='aux', dtype={'years_built':ARRAY(Float)})

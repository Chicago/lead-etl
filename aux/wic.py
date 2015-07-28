#!/usr/bin/python

import numpy as np
from lead.model import util
from lead.output.aggregate import aggregate
import pandas as pd

def psql_array(d):
    d = np.array(d, dtype=np.float)
    return d[~np.isnan(d)]

def array_to_dummies(df, column, dummy_lookup):
    for code,name in dummy_lookup.iteritems():
        df[column + '_'+ name.replace(' ', '_')] = df[column].apply(lambda d: code in d)

public_assistance_codes = {
    1:'MEDICAID',
    2:'FOOD STAMPS',
    3:'OTHER SERVICES PROVIDED',
    4:'SCHOOL SCHOOL LUNCH PROGRAM',
    5:'WEATHERIZATION',
    6:'THE EMGNCY FD ASST',
    7:'AFDC',
    8:'GENERAL ASSISTANCE',
    9:'HEAD START',
    10:'EARLY INTERVENTION',
    11:'MENTAL HEALTH',
    12:'ALCOHOL OR SUBSTANCE ABUSE',
    13:'DSCC',
    14:'DORS',
    15:'DCFS',
    16:'PUBLIC HOUSING',
    17:'DAY CARE',
    18:'TRANSPORTATION',
    19:'FAMILY PLANNING',
    20:'DOMESTIC VIOLENCE',
    21:'PARENTING EDUCATION',
    22:'EMERGENCY SHELTER',
    23:'JOB TRAINING',
    24:'VOCATIONAL EDUCATION',
    25:'CSFP MAC',
    26:'SCHOOL BREAKFAST PROGRAM',
    27:'SSI',
    28:'SSA',
    29:'PRIVATE PHYSICIAN',
    30:'STATE, COUNTY OR CITY HD',
    31:'INDIAN HEALTH SERVICE',
    32:'MIGRANT HEALTH SERVICE',
    33:'HMO',
    34:'COMMUNITY HEALTH CENTER',
    35:'NONE',
    36:'HOSPITAL OUTPATIENT CARE',
    37:'MILITARY',
    38:'TEMP ASST NEEDY FAMILY',
    99:'OTHER SOURCE OF CARE',
}

engine = util.create_engine()

wic = pd.read_sql("""
select cur_frst_t first_name, 
       cur_last_t last_name,
       birth_d::date as date_of_birth,
       nullif(hseh, 0) household_size,
       hse_inc_ household_income,
       array[pa_c1, pa_c2, pa_c3, pa_c4, pa_c5] as public_assistance,
       clinic
from input.wic
""", engine)

wic.public_assistance = wic.public_assistance.apply(psql_array)

wic_columns = {
    'count': {'numerator':1},
    'household_size_min': {'numerator': 'household_size', 'func':np.min},
    'household_size_max': {'numerator': 'household_size', 'func':np.max},
    'household_size_median': {'numerator': 'household_size', 'func':np.max},
    
    'household_income_min': {'numerator': 'household_income', 'func':np.min},
    'household_income_max': {'numerator': 'household_income', 'func':np.max},
    'household_income_median': {'numerator': 'household_income', 'func':np.max},
    
    'public_assistance': {'numerator':'public_assistance', 'func': lambda d: list(np.concatenate(d.values))},
}


wic_agg = aggregate(wic, wic_columns, index=['first_name', 'last_name','date_of_birth'])

array_to_dummies(wic_agg, 'public_assistance', public_assistance_codes)

wic_agg.drop('public_assistance', inplace=True, axis=1)

wic_agg.reset_index(inplace=True)
wic_agg.index.names=['id']

db = util.PgSQLDatabase(engine)
db.to_sql(frame = wic_agg, name='wic', schema='aux',if_exists='replace', index=True)

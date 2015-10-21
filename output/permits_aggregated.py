#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os
from itertools import product

from drain.util import create_engine, count_unique, execute_sql, PgSQLDatabase,prefix_columns, join_years
from drain.aggregate import aggregate, censor
from drain import data

from datetime import date

levels = ['address_id', 'building_id', 'complex_id', 'census_block_id', 'census_tract_id', 'ward_id']
deltas = [-1, 1, 3]
level_deltas = {level: deltas for level in levels}

PERMIT_TYPES = ['electric_wiring', 'elevator_equipment', 'signs', 'new_construction', 'renovation_alteration', 'easy_permit_process', 'porch_construction', 'wrecking_demolition', 'scaffolding', 'reinstate_revoked_pmt', 'for_extension_of_pmt']

def aggregate_permits(permits, levels):
    PERMIT_COLUMNS = {
        'count': {'numerator':1},
    }

    for permit_type in PERMIT_TYPES:
        PERMIT_COLUMNS['permit_type_' + permit_type] = { 'numerator' : 'permit_type_' + permit_type}
        PERMIT_COLUMNS['permit_type_' + permit_type + '_prop'] = { 'numerator' : 'permit_type_' + permit_type, 'denominator': 1}

    r = []
    for level in levels:
        df = aggregate(permits, PERMIT_COLUMNS, index=[level])
        df.reset_index(inplace=True)
        df['aggregation_level'] = level
        df.rename(columns={level:'aggregation_id'}, inplace=True)
        r.append(df)

    return pd.concat(r)

if __name__ == '__main__':
    engine = create_engine()
    db = PgSQLDatabase(engine)

    permits = pd.read_sql('select * from aux.building_permits', engine)
    permits['issue_date'] = pd.to_datetime(permits['issue_date'])

    addresses = pd.read_pickle(sys.argv[1])
    permits = permits.merge(addresses, how='inner', on='address',copy=False)

    end_dates = map(lambda y: np.datetime64(date(y,1,1)), range(2007, 2015))

    def aggregated_permits():
        for delta,end_date in product(deltas, end_dates):
            print end_date, delta
            censored_permits = censor(permits, 'issue_date', end_date, delta)
            df = aggregate_permits(censored_permits, levels)
            df['aggregation_end'] = end_date
            df['aggregation_delta']=delta
            yield df
    
    df = pd.concat(aggregated_permits())
        
    r = db.to_sql(df, 'permits_aggregated', if_exists='replace', schema='output', 
                  pk=['aggregation_end', 'aggregation_delta', 'aggregation_level', 'aggregation_id'], index=False)
    if r != 0:
        sys.exit(r)
        

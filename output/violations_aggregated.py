#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os
from itertools import product

from lead.model.util import create_engine, count_unique, execute_sql, PgSQLDatabase,prefix_columns, join_years
from lead.output.aggregate import aggregate, censor

from drain import data

from datetime import date

VIOLATION_KEYWORDS = ['water', 'paint', 'window', 'wall', 'porch']

def aggregate_violations(violations, levels):
    VIOLATION_COLUMNS = {
        'count': {'numerator':1},
    }

    for keyword in VIOLATION_KEYWORDS:
        VIOLATION_COLUMNS['keyword_' + keyword] = { 'numerator' : 'keyword_' + keyword}
        VIOLATION_COLUMNS['keyword_' + keyword + '_prop'] = { 'numerator' : 'keyword_' + keyword, 'denominator' : 1 }

    r = []
    for level in levels:
        df = aggregate(violations, VIOLATION_COLUMNS, index=[level])
        df.reset_index(inplace=True)
        df['aggregation_level'] = level
        df.rename(columns={level:'aggregation_id'}, inplace=True)
        r.append(df)

    return pd.concat(r)

if __name__ == '__main__':
    engine = create_engine()
    db = PgSQLDatabase(engine)

    violations = pd.read_sql("select address, violation_date, lower(violation_description) as violation_description from input.building_violations", engine).dropna()
    print len(violations)

    for keyword in VIOLATION_KEYWORDS:
        violations['keyword_' + keyword] = violations.violation_description.apply(lambda s: s.find(keyword) > -1)
    violations['violation_date'] = pd.to_datetime(violations['violation_date'])

    addresses = pd.read_pickle(sys.argv[1])
    violations = violations.merge(addresses, how='inner', on='address',copy=False)
    print len(violations)

    levels = ['address_id', 'building_id', 'complex_id', 'census_block_id', 'census_tract_id', 'ward_id']
    deltas = [-1,1,3]
    end_dates = map(lambda y: np.datetime64(date(y,1,1)), range(2007, 2015))

    def aggregated_violations():
        for delta,end_date in product(deltas, end_dates):
            print end_date, delta
            censored_violations = censor(violations, 'violation_date', end_date, delta)
            print len(censored_violations)
            df = aggregate_violations(censored_violations, levels)
            print len(df)
            df['aggregation_end'] = end_date
            df['aggregation_delta']=delta
            yield df
    
    df = pd.concat(aggregated_violations())
        
    r = db.to_sql(df, 'violations_aggregated', if_exists='replace', schema='output', 
                  pk=['aggregation_end', 'aggregation_delta', 'aggregation_level', 'aggregation_id'], index=False)
    if r != 0:
        sys.exit(r)

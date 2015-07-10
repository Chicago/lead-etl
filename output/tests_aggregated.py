#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os

from lead.model.util import create_engine, count_unique, execute_sql, PgSQLDatabase,prefix_columns
from lead.output.aggregate import aggregate

from datetime import date,timedelta
from dateutil.parser import parse

# does not modify passed tests dataframe
# optionally populate start_ and end_columns with start_ and end_dates
def censor_tests(tests, end_date):
    tests = tests[tests['test_date'] < end_date]
    
    to_revise = (tests['kid_max_date'] >= end_date)
    df = tests[to_revise]
    tests = tests[~to_revise] # these tests are fine, keep them to concat later
    df.drop(['kid_max_date','kid_max_bll', 'kid_minmax_date', 'kid_minmax_bll'], axis=1, inplace=True)
    
    # here max refers to maximum bll
    max_idx = df.groupby('kid_id')['test_bll'].idxmax()
    max_tests = df.ix[max_idx]
    max_tests = max_tests[['kid_id', 'test_bll','test_date']].rename(
            columns = {'test_bll': 'kid_max_bll', 'test_date':'kid_max_date'})
    df = df.merge(max_tests, on='kid_id')
    
    # here max_tests refers to tests at which a kid is at their max status (poisoned or not)
    max_tests = df[(df['test_bll'] > 5) == (df['kid_max_bll'] > 5)]
    minmax_idx = max_tests.groupby('kid_id')['test_kid_age_days'].idxmin()
    minmax_tests = max_tests.ix[minmax_idx]
    minmax_tests = minmax_tests[['kid_id', 'test_bll','test_date']].rename(
            columns={'test_bll': 'kid_minmax_bll', 'test_date':'kid_minmax_date'})
    
    df = pd.concat((tests, df.merge(minmax_tests, on='kid_id')))
        
    return df

# delta is number of days
# when delta is -1, aggregate all tests
def aggregate_tests(tests, level, today, delta):
    if delta != -1:
        start_date = date(end_date.year-delta, end_date.month, end_date.day)
        tests = tests[tests['test_date'] >= start_date]

    ebll_test_count = lambda t: (t.test_bll > 5).astype(int)
    ebll_kid_ids = lambda t: t.kid_id.where(t.test_bll > 5)

    TEST_COLUMNS = {
        'count': {'numerator': 1},
        'tested': {'numerator': 1, 'func': np.max},
        'poisoned': {'numerator': lambda t: (t.test_bll > 5).astype(int), 'func':np.max},

        'ebll_count': {'numerator': ebll_test_count},
        'ebll_prop': {'numerator': ebll_test_count, 'denominator': 1},

        'bll_avg': {'numerator': 'test_bll', 'func':np.mean},
        'bll_median': {'numerator': 'test_bll', 'func':np.median},
        'bll_max': {'numerator': 'test_bll', 'func':np.max},
        'bll_min': {'numerator': 'test_bll', 'func':np.min},
        'bll_std': {'numerator': 'test_bll', 'func':np.std},

        'kid_max_bll_avg': {'numerator': 'kid_max_bll', 'func':np.mean},
        'kid_max_bll_median': {'numerator': 'kid_max_bll', 'func':np.median},
        'kid_max_bll_max': {'numerator': 'kid_max_bll', 'func':np.max},
        'kid_max_bll_min': {'numerator': 'kid_max_bll', 'func':np.min},
        'kid_max_bll_std': {'numerator': 'kid_max_bll', 'func':np.std},
         
        'kid_count': {'numerator': 'kid_id', 'func':count_unique},
         # count number of kids with
        'kid_ebll_here_count': {'numerator': ebll_kid_ids, 'func': count_unique }, # ebll here
        'kid_ebll_first_count': {'numerator': lambda t: (t.test_minmax & (t.test_bll > 5))}, # first ebll here
        'kid_ebll_ever_count' : {'numerator': lambda t: t.kid_id.where( (t.kid_minmax_bll > 5) ), 'func': count_unique}, # ever ebll
        'kid_ebll_future_count': {'numerator': lambda t: t.kid_id.where( (t.kid_minmax_bll > 5) & (t.kid_minmax_date >= t.test_date) ), 'func': count_unique} # future ebll
    }

    df = aggregate(tests, TEST_COLUMNS, index=level)
    df['kid_ebll_here_prop'] = df['kid_ebll_here_count']/df['kid_count']
    df['kid_ebll_first_prop'] = df['kid_ebll_first_count']/df['kid_count']
    df['kid_ebll_ever_prop'] = df['kid_ebll_ever_count']/df['kid_count']
    df['kid_ebll_future_prop'] = df['kid_ebll_future_count']/df['kid_count']
  
    return df

if __name__ == '__main__':
    tests = pd.read_pickle(sys.argv[1])
    addresses = pd.read_pickle(sys.argv[2])
    tests = tests.merge(addresses, on='address_id')

    engine = create_engine()
    db = PgSQLDatabase(engine)

    year = int(sys.argv[3])
    end_date = date(year,1,1)

    censored_tests = censor_tests(tests, end_date)

    level_deltas = {
        'address_id': [-1] + range(1,11),
        'census_block_id': [-1] + range(1,11),
        'census_tract_id': [-1] + range(1,11),
    }
    
    execute_sql("delete from output.tests_aggregated where aggregation_end='{end_date}'".format(end_date=end_date), engine)

    for level,deltas in level_deltas.iteritems():
        for delta in deltas:
            print year, level, delta
            df = censored_tests[censored_tests[level].notnull()]
            df = aggregate_tests(df, level, end_date, delta)
            df.reset_index(inplace=True)
            df.rename(columns={level:'aggregation_id'}, inplace=True)
            df['aggregation_level'] = level
            df['aggregation_delta'] = delta
            df['aggregation_end'] = end_date
        
            r = db.to_sql(df, 'tests_aggregated', if_exists='append', schema='output', 
                          pk=['aggregation_end, aggregation_delta, aggregation_level, aggregation_id'], index=False)
            if r != 0:
                sys.exit(r)
        

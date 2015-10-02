#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os

from lead.model.util import create_engine, count_unique, execute_sql, PgSQLDatabase,prefix_columns
from lead.output.aggregate import aggregate

from datetime import date,timedelta
from dateutil.parser import parse

level_deltas = {
    'address_id': [-1] + [1,3,5,7],
    'building_id': [-1] + [1,3,5,7],
    'complex_id': [-1] + [1,3,5,7],
    'census_block_id': [-1] + [1,3,5,7],
    'census_tract_id': [-1] + [1,3,5,7],
}
# does not modify passed tests dataframe
# optionally populate start_ and end_columns with start_ and end_dates
def censor_tests(tests, end_date):
    tests = tests[tests['test_date'] < end_date]
    
    to_revise = (tests['kid_max_sample_date'] >= end_date)
    df = tests[to_revise]
    df.sort('test_date', inplace=True, ascending=True) # sort in place by date so ties in bll are broken by earliest test for max_test_date
    tests = tests[~to_revise] # these tests are fine, keep them to concat later
    df = df.drop(['kid_max_date','kid_max_bll', 'kid_minmax_date', 'kid_minmax_bll', 'kid_max_sample_date'], axis=1)

    # here a max is the maximum age at test
    max_idx = df.groupby('kid_id')['test_kid_age_days'].idxmax()
    max_tests = df.ix[max_idx]
    max_tests = max_tests[['kid_id', 'test_date']].rename(
            columns = {'test_date':'kid_max_sample_date'})
    df = df.merge(max_tests)
    
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

        # how old are these kids that are getting poisoned? TODO: create first_address variable so that these are not weighted by number of tests!
        'kid_ebll_minmax_age_mean': {'numerator': lambda t: t.kid_minmax_age_days.where(t.kid_minmax_bll > 5), 'func': 'mean'},
        'kid_ebll_minmax_age_median': {'numerator': lambda t: t.kid_minmax_age_days.where(t.kid_minmax_bll > 5), 'func': 'median'},

        # how old are these kids getting tested at?
        'kid_ebll_min_sample_age_mean': {'numerator': 'kid_min_sample_age_days', 'func': 'mean'},
        'kid_ebll_min_sample_age_median': {'numerator': 'kid_min_sample_age_days', 'func': 'median'},

        'kid_count': {'numerator': 'kid_id', 'func':count_unique},
        # count number of kids with
        'kid_ebll_here_count': {'numerator': ebll_kid_ids, 'func': count_unique }, # ebll here
        'kid_ebll_first_count': {'numerator': lambda t: (t.test_minmax & (t.test_bll > 5))}, # first ebll here
        'kid_ebll_ever_count' : {'numerator': lambda t: t.kid_id.where( (t.kid_minmax_bll > 5) ), 'func': count_unique}, # ever ebll
        'kid_ebll_future_count': {'numerator': lambda t: t.kid_id.where( (t.kid_minmax_bll > 5) & (t.kid_minmax_date >= t.test_date) ), 'func': count_unique}, # future ebll

        'address_count': {'numerator': 'address_id', 'func': count_unique},
        'address_ebll_count': {'numerator': lambda t: t.address_id.where(t.test_bll > 5), 'func': count_unique},
    }

    df = aggregate(tests, TEST_COLUMNS, index=level)
    df['kid_ebll_here_prop'] = df['kid_ebll_here_count']/df['kid_count']
    df['kid_ebll_first_prop'] = df['kid_ebll_first_count']/df['kid_count']
    df['kid_ebll_ever_prop'] = df['kid_ebll_ever_count']/df['kid_count']
    df['kid_ebll_future_prop'] = df['kid_ebll_future_count']/df['kid_count']
    df['address_ebll_prop'] = df['address_ebll_count']/df['address_count']
  
    return df

if __name__ == '__main__':
    tests = pd.read_pickle(sys.argv[1])
    addresses = pd.read_pickle(sys.argv[2])
    tests = tests.merge(addresses, on='address_id')

    engine = create_engine()
    db = PgSQLDatabase(engine)

    year = int(sys.argv[3])
    end_date = date(year,1,1)
    
    all_tests = tests
    tests = censor_tests(all_tests, end_date)

    tests['kid_minmax_age_days'] = (tests.kid_minmax_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    #tests['kid_max_age_days'] = (tests.kid_max_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    tests['kid_min_sample_age_days'] = (tests.kid_min_sample_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    #tests['kid_max_sample_age_days'] = (tests.kid_min_sample_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    
    #execute_sql("delete from output.tests_aggregated where aggregation_end='{end_date}'".format(end_date=end_date), engine)

    for level,deltas in level_deltas.iteritems():
        for delta in deltas:
            print year, level, delta

            # non-null level
            df = tests[tests[level].notnull()]
            # shortcut: only include it if it also occurs in the future
            df = df[df[level].isin( all_tests[all_tests.test_date >= end_date][level].unique() )]

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

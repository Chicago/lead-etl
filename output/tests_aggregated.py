#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os
from sqlalchemy.types import REAL,DATE,INTEGER,TEXT,DECIMAL
from lead.output.aggregations import level_index,indexes

from drain.util import create_engine, execute_sql, PgSQLDatabase,prefix_columns
from drain.aggregate import aggregate

from datetime import date,timedelta
from dateutil.parser import parse

aggregations = {
    'tract': [-1] + [1,3,5,7],
    'address': [-1] + [1,3,5,7],
    'building': [1], #[-1] + [1,3,5,7],
    'complex': [1], #[-1] + [1,3,5,7],
    'block': [-1] + [1,3,5,7],
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
def aggregate_tests(tests, index, today, delta):
    if delta != -1:
        start_date = date(end_date.year-delta, end_date.month, end_date.day)
        tests = tests[tests['test_date'] >= start_date]
    else:
        start_date = tests.test_date.min()

    TEST_COLUMNS = {
        'count': {'numerator': 1},
        'tested': {'numerator': 1, 'func': 'any'},

        'bll_mean': {'numerator': 'test_bll', 'func':'mean'},
        'bll_median': {'numerator': 'test_bll', 'func':'median'},
        'bll_max': {'numerator': 'test_bll', 'func':'max'},
        'bll_min': {'numerator': 'test_bll', 'func':'min'},
        'bll_std': {'numerator': 'test_bll', 'func':'std'},

        'kid_max_bll_mean': {'numerator': 'kid_max_bll', 'func':'mean'},
        'kid_max_bll_median': {'numerator': 'kid_max_bll', 'func':'median'},
        'kid_max_bll_max': {'numerator': 'kid_max_bll', 'func':'max'},
        'kid_max_bll_min': {'numerator': 'kid_max_bll', 'func':'min'},
        'kid_max_bll_std': {'numerator': 'kid_max_bll', 'func':'std'},

        # how old are these kids that are getting poisoned? TODO: create first_address variable so that these are not weighted by number of tests!
        'kid_ebll_minmax_age_median': {'numerator': lambda t: t.kid_minmax_age_days.where(t.kid_minmax_bll > 5), 'func': 'median'},
        'kid_ebll_minmax_age_mean': {'numerator': lambda t: t.kid_minmax_age_days.where(t.kid_minmax_bll > 5), 'func': 'mean'},
        # how old are these kids getting tested at?
        'kid_min_sample_age_median': {'numerator': 'kid_min_sample_age_days', 'func': 'median'},
        'kid_min_sample_age_mean': {'numerator': 'kid_min_sample_age_days', 'func': 'mean'},

        'kid_count': {'numerator': 'kid_id', 'func': 'nunique'},
        'family_count': {'numerator': 'kid_last_name', 'func': 'nunique'},

        # a kid is 'susceptible' in this period if they hadn't been poisoned by the start of the period
        'kid_susceptible_count': {'numerator': lambda t: t.kid_id.where( (t.kid_max_bll <= 5) | (t.kid_minmax_date >= start_date) ), 'func': 'nunique'},
        'address_tested_count': {'numerator': 'address_id', 'func': 'nunique'},

        'kid_24mo_count': {'numerator': lambda t: t.kid_id.where(
                (t.kid_max_sample_age_days > 30*24) | (t.kid_max_bll > 5)), 'func': 'nunique'}, # over 24mo or poisoned
        'kid_24mo_susceptible_count': {'numerator': lambda t: t.kid_id.where(
                ((t.kid_max_bll <= 5) | (t.kid_minmax_date >= start_date)) & # susceptible
                ((t.kid_max_sample_age_days > 30*24) | (t.kid_max_bll > 5)) ), # over 24mo or poisoned
                'func': 'nunique'},
    }

    # use a method because in a loop lambdas' references to threshold won't stick!
    def ebll_columns(threshold):
        ebll_test = lambda t: (t.test_bll > threshold)
        ebll_kid_ids = lambda t: t.kid_id.where(t.test_bll > threshold)

        bll = 'ebll%s' % threshold
        ebll_columns = {
            'poisoned_' + bll: {'numerator': ebll_test, 'func':'any'},
             bll+'_count': {'numerator': ebll_test},
            'family_' + bll +'_count': {'numerator': lambda t: t.kid_last_name.where( t.kid_max_bll > threshold), 'func': 'nunique'},
            'kid_' + bll + '_here_count': {'numerator': ebll_kid_ids, 'func': 'nunique' }, # ebll here
            'kid_' + bll + '_first_count': {'numerator': lambda t: (t.test_minmax & (t.test_bll > threshold))}, # first ebll here
            'kid_' + bll + '_ever_count' : {'numerator': lambda t: t.kid_id.where( (t.kid_minmax_bll > threshold) ), 'func': 'nunique'}, # ever ebll
            'kid_' + bll + '_future_count': {'numerator': lambda t: t.kid_id.where( (t.kid_minmax_bll > threshold) & (t.kid_minmax_date >= t.test_date) ), 'func': 'nunique'}, # future ebll
    
            'address_' + bll + '_count': {'numerator': lambda t: t.address_id.where(t.test_bll > threshold), 'func': 'nunique'},
        }
        TEST_COLUMNS.update(ebll_columns)

    for threshold in (5,10):
        ebll_columns(threshold)

    df = aggregate(tests, TEST_COLUMNS, index=index)

    for threshold in (5,10):
        bll = 'ebll%s' % threshold
        df[bll+'_prop'] = df[bll+'_count']/df['count']
    
        df['address_tested_'+bll+'_prop'] = df['address_'+bll+'_count']/df['address_tested_count']
        df['family_'+bll+'_prop'] = df['family_'+bll+'_count']/df['family_count']
    
        for age in ('', '24mo_'):
            df['kid_'+age+bll+'_here_prop'] = df['kid_'+bll+'_here_count']/df['kid_'+age+'count']
            df['kid_'+age+bll+'_ever_prop'] = df['kid_'+bll+'_ever_count']/df['kid_'+age+'count']
            df['kid_'+age+bll+'_future_prop'] = df['kid_'+bll+'_future_count']/df['kid_'+age+'susceptible_count']
            df['kid_'+age+bll+'_first_prop'] = df['kid_'+bll+'_first_count']/df['kid_'+age+'susceptible_count']

    df = df.astype(float, copy=False)
  
    df.reset_index(inplace=True)
    df.rename(columns={index:'aggregation_id'}, inplace=True)
    df['aggregation_level'] = indexes.index(index)
    df['aggregation_delta'] = delta
    df['aggregation_end'] = end_date

    return df

def aggregate_addresses(addresses, index):
    ADDRESS_COLUMNS={'residential_count':{'numerator':'address_residential', 'func':'sum'}}

    df = aggregate(addresses, ADDRESS_COLUMNS, index=index)
    df = df.astype(float, copy=False)

    df.reset_index(inplace=True)
    df.rename(columns={index:'aggregation_id'}, inplace=True)
    df['aggregation_level'] = indexes.index(index)
    
    return df

if __name__ == '__main__':
    tests = pd.read_pickle(sys.argv[1])
    addresses = pd.read_pickle(sys.argv[2])

    engine = create_engine()
    db = PgSQLDatabase(engine)

    year = int(sys.argv[3])
    end_date = date(year,1,1)
    
    tests = tests.merge(addresses, on='address_id', how='left')
    all_tests = tests # save all tests for shortcut below
    tests = censor_tests(tests, end_date)

    tests['kid_minmax_age_days'] = (tests.kid_minmax_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    tests['kid_min_sample_age_days'] = (tests.kid_min_sample_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    tests['kid_max_sample_age_days'] = (tests.kid_max_sample_date - tests.kid_date_of_birth) / np.timedelta64(1, 'D')
    residential = pd.concat( (aggregate_addresses(addresses, level_index(level)) for level in aggregations), copy=False)

    mode='w' # first write overwrites
    for level,deltas in aggregations.iteritems():
        for delta in deltas:
            print year, level, delta
            index = level_index(level)

            # non-null level
            df = tests[tests[index].notnull()]
            # shortcut: only include it if it also occurs in the future
            df = df[df[index].isin( all_tests[all_tests.test_date >= end_date][index].unique() )]
            df = aggregate_tests(df, index, end_date, delta)

            df = df.merge(residential, on=['aggregation_level', 'aggregation_id'])
            df['address_test_prop'] = df['address_tested_count'] / df['residential_count']
            df['address_ebll5_prop'] = df['address_ebll5_count'] / df['residential_count']
            df['address_ebll10_prop'] = df['address_ebll10_count'] / df['residential_count']

#            pk = {'aggregation_end':DATE, 'aggregation_delta':INTEGER, 'aggregation_level':TEXT, 'aggregation_id':DECIMAL}
#            dtype = {c:REAL for c in df.columns if c not in pk}
#            dtype.update(pk)
#            pk = str.join(',', pk.keys())


#            r = db.to_sql(df, 'tests_aggregated_temp', if_exists='append', schema='output', 
#                          pk=pk, dtype=dtype, index=False)
#            if r != 0:
#                sys.exit(r)
            df['aggregation_end'] = pd.to_datetime(df['aggregation_end'])
            df.to_hdf(sys.argv[4], 'df', mode=mode, append=True)
            mode = 'a'

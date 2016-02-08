from drain import data
from drain.data import FromSQL, Merge
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Aggregate, Aggregator

import pandas as pd
import logging

KIDS = FromSQL(table='output.kids', parse_dates=['date_of_birth', 
        'first_bll6_sample_date', 'first_bll10_sample_date', 
        'first_sample_date', 'last_sample_date'],
        to_str=['first_name', 'last_name'], target=True)

# need tests to revise kids
TESTS = FromSQL(table='output.tests', parse_dates=['sample_date'], 
        target=True)

ka = FromSQL(query="""
select kid_id, address_id, min_date, max_date from output.kid_addresses
""", parse_dates=['min_date', 'max_date'], target=True)
a = FromSQL(table='output.addresses', target=True)
KID_ADDRESSES = Merge(inputs=[ka, a])

# need wic_addresses (and tests) to revise kid_addresses
KID_WIC_ADDRESSES = FromSQL(table='aux.kid_wic_addresses', parse_dates=['date'], target=True)

def revise_kids(date):
    """
    Efficiently revise tests by only recalculating those aggregates that could have changed
    """
    logging.info('Revising kids %s' % date)
    tests = data.date_select(TESTS.get_result(), 'sample_date', date, 'all')
    kids = data.date_select(KIDS.get_result(), 'first_sample_date', date, 'all')

    to_revise = kids.last_sample_date >= date
    # drop the columns that need to be revised
    kids_to_revise = kids[to_revise].drop(
            ['max_bll', 'mean_bll', 'last_sample_date', 
            'address_count', 'test_count'], axis=1)
     
    tests_to_revise = tests[tests.kid_id.isin(kids_to_revise.kid_id)]

    # find last sample
    last_idx = tests_to_revise.groupby('kid_id')['age'].idxmax()
    last_tests = tests_to_revise.ix[last_idx]
    last_tests = last_tests[['kid_id', 'sample_date']].rename(
            columns={'sample_date':'last_sample_date'})
    kids_to_revise = kids_to_revise.merge(last_tests, on='kid_id')

    # count addresses and tests
    counts = tests_to_revise.groupby('kid_id').aggregate(
            {'bll': ['max', 'mean'], 'address_id':'nunique', 
             'test_id':'count'})
    counts.rename(columns={('bll', 'max'):'max_bll', 
            ('bll','mean'):'mean', 'address_id':'address_count', 
            'test_id':'test_count'}, inplace=True) 
    kids_revised = kids_to_revise.merge(counts, left_on='kid_id', right_index=True)

    data.date_censor(kids_revised, {'first_bll6_sample_date':[], 
            'first_bll10_sample_date':[]}, date)

    return pd.concat((kids[~to_revise], kids_revised))

def revise_kid_addresses(date):
    """
    Efficiently revise kid_addresses max_date
    """
    logging.info('Revising kid addresses %s' % date)
    kid_addresses = data.date_select(KID_ADDRESSES.get_result(), 'min_date', date, 'all')

    to_revise = kid_addresses.max_date >= date
    kid_addresses_to_revise = kid_addresses[to_revise].drop(['max_date'], axis=1)
    dates = pd.concat((TESTS.get_result()[['kid_id', 'address_id', 'sample_date']],
            KID_WIC_ADDRESSES.get_result().rename(columns={'date':'sample_date'})))

    dates_to_revise = dates[dates.kid_id.isin(kid_addresses[to_revise].kid_id) & 
          dates.address_id.isin(kid_addresses[to_revise].address_id) &
          (dates.sample_date < date)]

    max_date = dates_to_revise.groupby(['kid_id', 'address_id']).aggregate(
            {'sample_date':'max'})
    # TODO: get the mean bll at this address for this kid here! add that to output.kid_addresses, too.
    max_date.rename(columns={'sample_date':'max_date'}, inplace=True)
    kid_addresses_revised = kid_addresses_to_revise.merge(max_date, left_on=['kid_id', 'address_id'], right_index=True)

    return pd.concat((kid_addresses[~to_revise], kid_addresses_revised))

    # drop the columns that need to be revised
class KidsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self, aggregator_args=['index','date','delta'],
            spacedeltas=spacedeltas, dates=dates, prefix='kids',
            date_column='min_date', **kwargs)

        if not self.parallel:
            self.inputs = [TESTS, KID_ADDRESSES, KID_WIC_ADDRESSES, KIDS]

        self.data_revised = {}
            
    def get_data(self, index, date, delta):
        # cache revision based on date because it doesn't depend on index, delta
        if date in self.data_revised:
            kids, kid_addresses = self.data_revised[date]
        else:
            kids = revise_kids(date)
            kid_addresses = revise_kid_addresses(date)
            self.data_revised[date] = (kids, kid_addresses)

        if index != 'address':
            kid_addresses = kid_addresses.groupby(
                ['kid_id', self.spacedeltas[index][0]]
            ).aggregate({'min_date':'min', 'max_date':'max'}).reset_index()

        r = kid_addresses.merge(kids, on='kid_id')
        r = data.date_select(r, 'max_date', date=date, delta=delta)
        return r

    def get_aggregator(self, index, date, delta):
        df = self.get_data(index, date, delta)
        aggregator = Aggregator(df, self.get_aggregates(index, date, delta))
        return aggregator

    def get_aggregates(self, index, date, delta):
        aggregates = [
                Count(),
                Aggregate(['max_bll', 'mean_bll'], ['mean', 'median']),
                Count([lambda k: k.first_bll6_sample_date.notnull(), 
                        lambda k: k.first_bll10_sample_date.notnull()],
                        ['bll6_ever', 'bll10_ever'], prop=True),
                Count([lambda k: k.first_bll6_sample_date > k.max_date,
                        lambda k: k.first_bll10_sample_date > k.max_date],
                        ['bll6_future', 'bll10_future'], prop=True),
                Count([lambda k: k.first_bll6_sample_date < k.min_date,
                        lambda k: k.first_bll10_sample_date < k.min_date],
                        ['bll6_past', 'bll10_past'], prop=True),
                Count([lambda k: k.first_bll6_sample_date.between(k.min_date, k.max_date),
                        lambda k: k.first_bll10_sample_date.between(k.min_date, k.max_date)],
                        ['bll6_present', 'bll10_present'], prop=True),
                # TODO: family count
                # TODO: min_last_sample_age cutoffs
        ]
        return aggregates

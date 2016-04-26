from drain import data
from drain.data import FromSQL, Merge, Revise
from drain.util import day
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Fraction, Count, Aggregate, Aggregator, days

import os
import pandas as pd
import numpy as np
import logging

KIDS_PARSE_DATES = ['date_of_birth', 
        'first_wic_date', 'last_wic_date',
        'first_bll6_sample_date', 'first_bll10_sample_date', 
        'first_sample_date', 'last_sample_date', 
        'min_date', 'max_date']

KID_ADDRESSES_PARSE_DATES = ['address_min_date', 'address_max_date', 
        'address_wic_min_date', 'address_wic_max_date', 
        'address_test_min_date', 'address_test_max_date']

def revise_kid_addresses(date):
        kid_addresses_filename = os.path.join(
                os.path.dirname(__file__), 'kid_addresses.sql')
        kid_addresses = Revise(sql=kid_addresses_filename,
                id_column=['kid_id', 'address_id'], 
                max_date_column='address_max_date', 
                min_date_column='address_min_date', 
                date_column='date',
                date=date,
                from_sql_args={'parse_dates':KID_ADDRESSES_PARSE_DATES,
                               'target':True})
        kids_filename = os.path.join(
                os.path.dirname(__file__), 'kids.sql')
        kids = Revise(sql=kids_filename, 
                id_column='kid_id', 
                max_date_column = 'max_date', 
                min_date_column='min_date', 
                date_column='date',
                date=date, 
                from_sql_args={'parse_dates':KIDS_PARSE_DATES, 
                               'to_str':['first_name','last_name'],
                               'target':True})
        
        return Merge(inputs=[kids, kid_addresses], on='kid_id')

class KidsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self, spacedeltas=spacedeltas, 
            dates=dates, prefix='kids',
            aggregator_args=['date', 'index', 'delta'],
            date_column='address_min_date', **kwargs)

        if not self.parallel:
            kid_addresses = revise_kid_addresses(date=dates[0])
            addresses = FromSQL(table='output.addresses', target=True)
            self.inputs = [Merge(inputs=[kid_addresses, addresses], 
                    on='address_id')]

    def get_aggregator(self, date, index, delta):
        df = self.get_data(date, delta)
        if index == 'kid':
            df = df[((df.date_of_birth - date)/day).between(-366,366)]
        aggregator = Aggregator(df, 
                self.get_aggregates(date, index, delta))
        return aggregator

    def get_aggregates(self, date, index, delta):
        if index == 'kid':
            return [
                Aggregate(['address_count', 'test_count'],
                        'max', fname=False),
                Aggregate(['max_bll'], 'max', fname=False),
                Aggregate(lambda k: k.last_wic_date == k.address_wic_max_date, 
                        'any', 'last_wic_address', fname=False),
                Aggregate(['address_wic_mother', 'address_wic_infant'], 'any', fname=False),
                Aggregate([days('address_wic_max_date', date),
                        days('address_wic_min_date', date),
                        days('last_wic_date', date),
                        days('first_wic_date', date)],
                        ['max'], ['address_wic_min_date', 'address_wic_max_date', 
                                  'last_wic_date', 'first_wic_date'], fname=False)
            ]

        sample_2y = lambda k: ((k.last_sample_date - k.date_of_birth)/day > 365*2) | (k.max_bll >= 6)
        counts = Count([np.float32(1), sample_2y], ['kid', 'kid_sample_2y'])

        aggregates = [
            counts,
            Aggregate(['address_count', 'test_count'], 
                    ['median', 'mean', 'min', 'max']),

            Count([lambda k: k.address_test_min_date.notnull(), 
                   lambda k: k.first_sample_date.notnull(),
                   lambda k: k.first_wic_date.notnull()], prop=True, 
                  name=['tested_here', 'tested_ever', 'wic']),

            Count([lambda k: k.address_wic_min_date.notnull() & k.address_test_min_date.notnull(),
                   lambda k: k.address_wic_min_date.notnull() & k.first_sample_date.notnull()],
                   name=['wic_tested_here', 'wic_tested_ever'], 
                   prop=lambda k: k.first_wic_date.notnull(), prop_name='wic'),

            Aggregate([days('address_min_date', 'address_max_date'), 
                       days('address_wic_min_date', 'address_wic_max_date'), 
                       days('address_test_min_date', 'address_test_max_date')],
                       ['mean'], ['address_total_time', 'address_wic_time', 'address_test_time']),

            Aggregate(['max_bll', 'mean_bll', 'address_max_bll', 'address_mean_bll'], 
                    ['mean', 'median', 'min', 'max']),

            Fraction(Count([lambda k: k.first_bll6_sample_date.notnull(), 
                            lambda k: k.first_bll10_sample_date.notnull()],
                           ['bll6_ever', 'bll10_ever']),
                     counts, include_numerator=True),
            Fraction(Count([lambda k: k.first_bll6_sample_date > k.address_max_date,
                            lambda k: k.first_bll10_sample_date > k.address_max_date],
                           ['bll6_future', 'bll10_future']),
                     counts, include_numerator=True),
            Fraction(Count([lambda k: k.first_bll6_sample_date < k.address_min_date,
                    lambda k: k.first_bll10_sample_date < k.address_min_date],
                    ['bll6_past', 'bll10_past']), 
                    counts, include_numerator=True),
            Fraction(Count([lambda k: k.first_bll6_sample_date.between(
                            k.address_min_date, k.address_max_date),
                    lambda k: k.first_bll10_sample_date.between(
                            k.address_min_date, k.address_max_date)],
                    ['bll6_present', 'bll10_present']), 
                    counts, include_numerator=True),
            Aggregate('last_name', 'nunique', fname='count', astype=str)
            # TODO: min_last_sample_age cutoffs
        ]
        if delta == 'all':
            aggregates.extend([
                Aggregate(days('address_wic_min_date', date), ['min', 'max'], 'days_since_wic'),
                Aggregate(days('date_of_birth', date), ['min', 'max', 'mean'], 'date_of_birth'),
            ])

        return aggregates

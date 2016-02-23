from drain import data
from drain.data import FromSQL, Merge, Revise
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Aggregate, Aggregator

import os
import pandas as pd
import logging

KIDS_PARSE_DATES = ['date_of_birth', 
        'first_bll6_sample_date', 'first_bll10_sample_date', 
        'first_sample_date', 'last_sample_date']

KID_ADDRESSES_PARSE_DATES = ['address_min_date', 'address_max_date', 
        'address_wic_min_date', 'address_wic_max_date', 
        'address_test_min_date', 'address_test_max_date']


class KidsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self, spacedeltas=spacedeltas, 
            dates=dates, prefix='kids',
            date_column='address_min_date', **kwargs)

        if not self.parallel:
            kid_addresses_filename = os.path.join(os.path.dirname(__file__), 'kid_addresses.sql')
            kid_addresses = Revise(sql_filename=kid_addresses_filename, id_column='kid_id', 
                    max_date_column='address_max_date', min_date_column='address_min_date', 
                    date=self.dates[0], from_sql_args={'parse_dates':KID_ADDRESSES_PARSE_DATES,
                                                       'target':True})

            kids_filename = os.path.join(os.path.dirname(__file__), 'kids.sql')
            kids = Revise(sql_filename=kids_filename, id_column='kid_id', 
                    max_date_column = 'last_sample_date', min_date_column='first_sample_date', 
                    date=dates[0], from_sql_args={'parse_dates':KIDS_PARSE_DATES, 
                                                  'to_str':['first_name','last_name'],
                                                  'target':True})
            
            kids_merged = Merge(inputs=[kids, kid_addresses], on='kid_id')
            addresses = FromSQL(table='output.addresses', target=True)

            self.inputs = [Merge(inputs=[kids_merged, addresses], on='address_id')]

    def get_aggregates(self, date, delta):
        aggregates = [
                Count(),
                Aggregate(['max_bll', 'mean_bll'], ['mean', 'median']),
                Count([lambda k: k.first_bll6_sample_date.notnull(), 
                        lambda k: k.first_bll10_sample_date.notnull()],
                        ['bll6_ever', 'bll10_ever'], prop=True),
                Count([lambda k: k.first_bll6_sample_date > k.address_max_date,
                        lambda k: k.first_bll10_sample_date > k.address_max_date],
                        ['bll6_future', 'bll10_future'], prop=True),
                Count([lambda k: k.first_bll6_sample_date < k.address_min_date,
                        lambda k: k.first_bll10_sample_date < k.address_min_date],
                        ['bll6_past', 'bll10_past'], prop=True),
                Count([lambda k: k.first_bll6_sample_date.between(
                                k.address_min_date, k.address_max_date),
                        lambda k: k.first_bll10_sample_date.between(
                                k.address_min_date, k.address_max_date)],
                        ['bll6_present', 'bll10_present'], prop=True),
                # TODO: family count
                # TODO: min_last_sample_age cutoffs
                # TODO: days since last kid. days since last poisoning.
        ]
        return aggregates

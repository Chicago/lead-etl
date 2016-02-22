from drain import data
from drain.data import FromSQL, Merge, Revise
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Aggregate, Aggregator

import os
import pandas as pd
import logging

def kid_addresses_step(date):
    sql_filename = os.path.join(os.path.dirname(__file__), 'kid_addresses.sql')
    return Revise(sql_filename=sql_filename, id_column='kid_id', max_date_column = 'address_max_date', 
            min_date_column='address_min_date', date=date)

def kids_step(date):
    sql_filename = os.path.join(os.path.dirname(__file__), 'kids.sql')

    return Revise(sql_filename=sql_filename, id_column='kid_id', max_date_column = 'last_sample_date', 
            min_date_column='first_sample_date', date=date)

class KidsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self, aggregator_args=['index','date','delta'],
            spacedeltas=spacedeltas, dates=dates, prefix='kids',
            date_column='address_min_date', **kwargs)

        if not self.parallel:
            kids = kids_step(self.dates[0])
            kid_addresses = kid_addresses_step(self.dates[0])
            self.inputs = [Merge(inputs=[kids, kid_addresses], on='kid_id')]
#           self.inputs = [TESTS, KID_ADDRESSES, KID_WIC_ADDRESSES, KIDS]

#        self.data_revised = {}
#            
#    def get_data(self, index, date, delta):
#        # cache revision based on date because it doesn't depend on index, delta
#        if date in self.data_revised:
#            kids, kid_addresses = self.data_revised[date]
#        else:
#            kids = revise_kids(date)
#            kid_addresses = revise_kid_addresses(date)
#            self.data_revised[date] = (kids, kid_addresses)
#
#        if index != 'address':
#            kid_addresses = kid_addresses.groupby(
#                ['kid_id', self.spacedeltas[index][0]]
#            ).aggregate({'address_min_date':'min', 
#                    'address_max_date':'max'}).reset_index()
#
#        r = kid_addresses.merge(kids, on='kid_id')
#        r = data.date_select(r, 'address_max_date', date=date, delta=delta)
#        return r
#
#    def get_aggregator(self, index, date, delta):
#        df = self.get_data(index, date, delta)
#        aggregator = Aggregator(df, self.get_aggregates(index, date, delta))
#        return aggregator

    def get_aggregates(self, index, date, delta):
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

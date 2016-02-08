from drain import data
from drain.data import FromSQL, Merge
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Fraction, Aggregate

import pandas as pd
import logging

# TODO: make this more efficient by not including unnecessary address columns
tests = FromSQL(table='output.tests', parse_dates=['sample_date'], 
        target=True)
addresses = FromSQL(table='output.addresses', target=True)

def censor(tests, date, delta):
    logging.info('Censoring tests %s %s' % (date, delta))
    tests = data.date_select(tests, 'sample_date', date, delta)
    tests = data.date_censor(tests.copy(), 
            {'first_bll6_sample_date':[], 'first_bll10_sample_date':[]}, date)
    return tests

class TestsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
            spacedeltas=spacedeltas, dates=dates, prefix='tests',
            date_column='sample_date', **kwargs)

        if not self.parallel:
            self.inputs = [Merge(inputs=[tests, addresses], on='address_id')]

        self.revised_data = {}
            
    def get_aggregates(self, date, delta):
        bll6 = lambda t: t.bll > 5
        bll10 = lambda t: t.bll > 9
        kid_count = Aggregate('kid_id', 'nunique', 
                name='kid_count', fname=False)

        aggregates = [
            Count(),
            Aggregate('bll', ['mean', 'median', 'max', 'min', 'std']),
            kid_count,
            Fraction(Count(['first_bll6', 'first_bll10']),
                    kid_count, include_numerator=True)
        ]

        return aggregates

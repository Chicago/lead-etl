from drain import data
from drain.util import day
from drain.data import FromSQL, Merge
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Fraction, Aggregate, days

import pandas as pd
import logging

# TODO: make this more efficient by not including unnecessary address columns
class TestsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
            spacedeltas=spacedeltas, dates=dates, prefix='tests',
            date_column='date', **kwargs)

        if not self.parallel:
            self.inputs = [Merge(inputs=[
                    FromSQL(table='output.tests', parse_dates=['date'], target=True), 
                    FromSQL(table='output.addresses', target=True)], on='address_id')]

    def get_aggregates(self, date, delta):
        kid_count = Aggregate('kid_id', 'nunique', 
                name='kid_count', fname=False)

        aggregates = [
            Count(),
            Aggregate('bll', ['mean', 'median', 'max', 'min', 'std']),
            Aggregate(lambda t: t.bll.where(t.increase), ['mean', 'median', 'max', 'min', 'std'], 'increase_bll'),
            Count(lambda t: t.bll <= 2, 'bll2', prop=True),
            Fraction(Count(['first_bll6', 'first_bll10']), kid_count, 
                    include_numerator=True, include_denominator=True),
        ]
        if delta == 'all':
            aggregates.extend([
                Aggregate(days('date',date), ['min','max'], 
                        'days_since_test'),
                Aggregate([
                    lambda t: (date - t.date.where(t.bll >= 6))/day,
                    lambda t: (date - t.date.where(t.bll >= 10))/day],
                    ['min','max'], ['days_since_bll6', 'days_since_bll10'])
            ])
        return aggregates

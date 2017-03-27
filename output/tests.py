from drain import data
from drain.util import day
from drain.data import FromSQL, Merge
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Fraction, Aggregate, days

import pandas as pd

tests = Merge(inputs=[
    Merge(inputs=[
        FromSQL(table='output.tests', parse_dates=['date']), 
        FromSQL(table='output.addresses')], on='address_id'),
    # get kid first bll6 and bll10 counts to calculate incidences
    FromSQL("""
        select kid_id, first_bll6_sample_date, first_bll10_sample_date 
        from output.kids
    """, parse_dates=['first_bll6_sample_date', 'first_bll10_sample_date'])],
on='kid_id')
tests.target = True

class TestsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, parallel=False):
        SpacetimeAggregation.__init__(self,
            inputs = [tests],
            spacedeltas=spacedeltas, 
            parallel=parallel,
            dates=dates, prefix='tests',
            date_column='date', censor_columns={'first_bll6_sample_date':[], 
                                                'first_bll10_sample_date':[]})

    def get_aggregates(self, date, delta):
        kid_count = Aggregate('kid_id', 'nunique', 
                name='kid_count', fname=False)

        aggregates = [
            Count(),
            Aggregate('bll', ['mean', 'median', 'max', 'min', 'std']),
            Aggregate(lambda t: t.bll.where(t.increase), ['mean', 'median', 'max', 'min', 'std'], 'increase_bll'),
            Count(lambda t: t.bll <= 2, 'bll2', prop=True),
            # prevalences
            Fraction(Count(['first_bll6', 'first_bll10']), kid_count, 
                    include_numerator=True, include_denominator=True),
        ]

        # incidences
        if delta != 'all':
            start_date = date - data.parse_delta(delta)
            no_bll6_count = Aggregate(lambda k: k.kid_id.where((k.first_bll6_sample_date >= start_date).fillna(True)), 
                    'nunique', name='no_bll6_count', fname=False)
            no_bll10_count = Aggregate(lambda k: k.kid_id.where((k.first_bll10_sample_date >= start_date).fillna(True)), 
                    'nunique', name='no_bll10_count', fname=False)

            aggregates.extend([
                no_bll6_count, 
                no_bll10_count,
                Count('first_bll6')/no_bll6_count, 
                Count('first_bll10')/no_bll10_count])


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

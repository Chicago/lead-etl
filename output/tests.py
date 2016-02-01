from drain import data
from drain.data import FromSQL
from drain.step import Step
from drain.aggregation import SpacetimeAggregation
from drain.aggregate import Count, Aggregate

import pandas as pd
import logging

class Tests(Step):
    def __init__(self, **kwargs):
        Step.__init__(self, **kwargs)
        self.inputs = [FromSQL(
            query="""select *, sample_date - date_of_birth as age
                     from output.tests join output.kids using (kid_id)""",
            parse_dates=['sample_date', 'date_of_birth', 
                'first_bll6_sample_date', 'first_bll10_sample_date', 
                'first_sample_date', 'last_sample_date'],
            to_str=['first_name', 'last_name'], target=True)]

    def censor(self, date, delta):
        logging.info('Censoring tests %s %s' % (date, delta))
        tests = self.inputs[0].get_result()
        tests = data.date_select(tests, 'sample_date', date, delta)
        tests = data.date_censor(tests.copy(), 
                {'first_bll6_sample_date':[], 'first_bll10_sample_date':[]}, date)

        to_revise = tests.last_sample_date >= date
        df = tests[to_revise]
        # drop the columns that need to be revised
        df = df.drop(['max_bll', 'last_sample_date', 'address_count', 'test_count'], axis=1)
        
        # find max bll
        max_idx = df.groupby('kid_id')['bll'].idxmax()
        max_tests = df.ix[max_idx]
        max_tests = max_tests[['kid_id', 'bll']].rename(columns={'bll':'max_bll'})
        df = df.merge(max_tests, on='kid_id')

        # find last sample
        last_idx = df.groupby('kid_id')['age'].idxmax()
        last_tests = df.ix[last_idx]
        last_tests = last_tests[['kid_id', 'sample_date']].rename(
                columns={'sample_date':'last_sample_date'})
        df = df.merge(last_tests, on='kid_id')

        # count addresses and tests
        counts = df.groupby('kid_id').aggregate({'address_id':'nunique', 'test_id':'count'})
        counts.columns = ['address_count', 'test_count']
        df = df.merge(counts, left_on='kid_id', right_index=True)

        return pd.concat((tests[~to_revise], df))


class TestsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
            spacedeltas = spacedeltas, dates = dates, prefix = 'tests',
            date_column = 'sample_date', **kwargs)

        if not self.parallel:
            self.inputs = [Tests()]
            
    # TODO add tests as input and do censoring and feature generation on given thresholds (a parameter)

    def get_data(self, date, delta):
        return self.inputs[0].censor(date, delta)

    def get_aggregates(self, date, delta):
        aggregates = [
            Count(),
            Aggregate('bll', ['mean', 'median', 'max', 'min', 'std']),
#            Aggregate('kid_mean_bll', ['mean', 'median', 'max', 'min', 'std']),
            Aggregate('max_bll', ['mean', 'median', 'max', 'min', 'std']),

#            Aggregate('kid_first_ebll_age', ['mean', 'median']),
#            Aggregate('kid_first_sample_age', ['mean', 'median']),

            Aggregate('kid_id', 'nunique'),
            Aggregate('last_name', 'nunique'),
        ]

        return aggregates

        # use a method because in a loop lambdas' references to threshold won't stick!
    def get_ebll_aggregates(self, threshold):
        ebll_test = lambda t: (t.test_bll > threshold)
        ebll_kid_ids = lambda t: t.kid_id.where(t.test_bll > threshold)

        bll = 'ebll%s' % threshold
        return [
            Aggregate(ebll_test, ['any', 'test'], name=bll),
            Aggregate(lambda t: t.kid_last_name.where(t.test_bll > threshold),
                'nunique', 'family_' + bll),
            Count('first_%s' % bll, name=bll+'_here'),
            Aggregate(lambda t: t.kid_id.where(t.kid_max_bll > threshold),
                'nunique', 'kid_' + bll + '_ever'),
            Aggregate(lambda t: t.kid_id.where(
                    t['kid_first_%s_date' % bll] > t.sample_date),
                'nunique', 'kid_' + bll + '_future'),
        ]

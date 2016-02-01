import os
import logging
from datetime import date

import pandas as pd
import numpy as np

from drain import util, aggregate, data
from drain.step import Step
from drain.aggregate import Aggregate, Count, aggregate_counts
from drain.aggregation import SpacetimeAggregation
from drain.data import FromSQL

day = np.timedelta64(1, 'D')
CLOSURE_CODES = list(set(range(0,14)).difference({2,9}))

class Inspections(Step):
    def __init__(self, date, **kwargs):
        Step.__init__(self, date=date, **kwargs)
        self.inputs = [FromSQL(query="""
select *, least(init_date, comply_date) as min_date
from output.inspections join output.addresses using (address_id) 
where least(init_date, comply_date) < '%s'""" % date)]

    def run(self, df):
        # TODO: verify and explain why fillna(True)
        df.hazard_ext.fillna(True, inplace=True)
        df.hazard_int.fillna(True, inplace=True)
        df['hazard'] = df.hazard_ext | df.hazard_int
        df['hazard_both'] = df.hazard_ext & df.hazard_int
        df['complied'] = df.comply_date.notnull()
        df['inspected'] = df.comply_date.notnull()
        df['inspection_to_compliance'] = (df['comply_date'] - df['init_date']) / day

        return df
        

class InspectionsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        kwargs['inputs'] = []
        SpacetimeAggregation.__init__(self,
                spacedeltas = spacedeltas,
                dates = dates,
                prefix = 'inspections',
                date_column = 'min_date', 
                censor_columns = 
                    {'comply_date':['closure', 'complied', 
                                    'inspection_to_compliance' ],
                     'init_date':['inspected']}, **kwargs)

        if not self.parallel:
            self.inputs = [Inspections(max(dates))]

        self.dtypes = np.float32


    def get_aggregates(self, date, delta):
        
        aggregates = [
            Count(), 
            Aggregate('inspected', 'max', function_names=False),
            Aggregate('complied', 'max', function_names=False),

            Count('hazard_int', prop=True), Count('hazard_ext', prop=True),
            Count('hazard', prop=True), Count('hazard_both', prop=True),

            Count('complied', prop=True),

            Aggregate('inspection_to_compliance', ['mean', 'min', 'max']),
            Aggregate(lambda i: (date - i.init_date)/day, ['mean', 'min', 'max'],
                    name='from_inspection'),
            Aggregate(lambda i: (date - i.comply_date)/day, ['mean', 'min', 'max'],
                    name='from_compliance'),
        ]

        aggregates.extend([Count(lambda i: i['closure'] == c, name='closure_%s' % c, prop=True) for c in CLOSURE_CODES])
       
        return aggregates

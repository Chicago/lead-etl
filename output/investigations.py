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
CLOSURE_CODES = range(1,12+1)
DATE_COLUMNS = ['referral_date', 'init_date', 'comply_date', 'closure_date']
DATE_NAMES = ['referral', 'inspection', 'compliance', 'closure']

class Inspections(Step):
    def __init__(self, **kwargs):
        Step.__init__(self, **kwargs)
        self.inputs = [FromSQL(query="""
        select * 
        from output.investigations join output.addresses using (address_id)
        where -- ensure referral_date <= init_date <= comply_date <= closure_date
            coalesce(referral_date <= least(init_date, comply_date, closure_date), true) 
            and coalesce(init_date <= least(comply_date, closure_date), true)
            and coalesce(comply_date <= closure_date, true)
        """, parse_dates=DATE_COLUMNS,
        tables=['output.investigations', 'output.addresses'], target=False)]

    def run(self, df):
        df['hazard'] = df.hazard_ext | df.hazard_int
        df['hazard_both'] = df.hazard_ext & df.hazard_int
        df['complied'] = df.comply_date.notnull()
        df['inspected'] = df.init_date.notnull()

        df['referral_to_inspection'] = (df['init_date'] - df['referral_date']) / day
        df['referral_to_compliance'] = (df['comply_date'] - df['referral_date']) / day
        df['referral_to_closure'] = (df['closure_date'] - df['referral_date']) / day

        df['inspection_to_compliance'] = (df['comply_date'] - df['init_date']) / day
        df['inspection_to_closure'] = (df['closure_date'] - df['init_date']) / day

        df['compliance_to_closure'] = (df['closure_date'] - df['comply_date']) / day

        return df

class InvestigationsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
                spacedeltas = spacedeltas,
                dates = dates,
                prefix = 'investigations',
                date_column = 'referral_date', 
                censor_columns = {
                    'comply_date':['complied', 'referral_to_compliance', 
                            'inspection_to_compliance' ],
                    'init_date':['inspected', 'referral_to_inspection', 
                            'inspection_to_compliance']
                }, 
                **kwargs)

        if not self.parallel:
            self.inputs = [Inspections(target=True)]

    def get_aggregates(self, date, delta):
        
        aggregates = [
            Count(), 
            Aggregate('inspected', 'max', fname=False),
            Aggregate('complied', 'max', fname=False),

            Count('hazard_int', prop=True), Count('hazard_ext', prop=True),
            Count('hazard', prop=True), Count('hazard_both', prop=True),

            Count('inspected', prop=True),
            Count('complied', prop=True),

            Aggregate(['referral_to_inspection', 'referral_to_compliance', 
                        'referral_to_closure', 'inspection_to_compliance', 
                        'inspection_to_closure', 'compliance_to_closure'], 
                ['mean', 'min', 'max']),
            Aggregate([lambda i, d=d: (date - i[d])/day for d in DATE_COLUMNS],
                    ['mean', 'min', 'max'],
                    name=['since_%s' % d for d in DATE_NAMES]),
        ]

        aggregates.extend([Count(lambda i,c=c: i['closure_code'] == c, name='closure_code_%s' % c, prop=True) for c in CLOSURE_CODES])
       
        return aggregates

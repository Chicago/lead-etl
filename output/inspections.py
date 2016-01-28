import os
import logging
from datetime import date

import pandas as pd
import numpy as np

from drain import util, aggregate, data
from drain.aggregate import Aggregate, Count, aggregate_counts, SpacetimeAggregator, Spacedeltas

day = np.timedelta64(1, 'D')
CLOSURE_CODES = list(set(range(0,14)).difference({2,9}))

deltas = ['all','1y','3y']
spaces = {	'address':'address_id','building': 'building_id', 
			'complex':'complex_id', 'block':'census_block_id',
			'tract':'census_tract_id', 'ward':'ward_id'}

class InspectionsAggregator(SpacetimeAggregator):
    def __init__(self, basedir, psql_dir=''):
        SpacetimeAggregator.__init__(self, 
                spacedeltas = { space:	Spacedeltas(index,deltas) for space,index in spaces.iteritems() },
                dates = [date(y,1,1) for y in xrange(2000,2015+1)],
                prefix = 'inspections',
                basedir = basedir,
                date_col = 'min_date', censor_cols={'comply_date':['closure', 'complied', 'from_inspection', 'from_compliance', 'inspection_to_compliance'], 'init_date':['inspected']})

        self.DEPENDENCIES = [os.path.join(psql_dir, 'output/inspections')]
        self.dtypes = np.float32

    def get_data(self, date):
        engine = util.create_engine()
        logging.info('Reading inspections %s' % date)
        df = pd.read_sql("select *, least(init_date, comply_date) as min_date from output.inspections join output.addresses using (address_id) where least(init_date, comply_date) < '%s'" % date, engine, parse_dates=['min_date', 'init_date', 'comply_date'])

        # TODO: verify and explain why fillna(True)
        df.hazard_ext.fillna(True, inplace=True)
        df.hazard_int.fillna(True, inplace=True)
        df['hazard'] = df.hazard_ext | df.hazard_int
        df['hazard_both'] = df.hazard_ext & df.hazard_int
        df['complied'] = df.comply_date.notnull()
        df['inspected'] = df.comply_date.notnull()

        dt = df['comply_date'] - df['init_date']
        df['inspection_to_compliance'] = dt[dt.notnull()] / day
        df['from_inspection'] = (date - df['init_date'] )/day
        df['from_compliance'] = (date - df['comply_date'] )/day

        return df

    def get_aggregates(self, date, data):
        
        aggregates = [
            Count(), 
            Aggregate('inspected', 'max', function_names=False),
            Aggregate('complied', 'max', function_names=False),

            Count('hazard_int', prop=True), Count('hazard_ext', prop=True),
            Count('hazard', prop=True), Count('hazard_both', prop=True),

            Count('complied', prop=True),
            Aggregate('inspection_to_compliance', ['mean', 'min', 'max']),
            Aggregate('from_inspection', ['mean', 'min', 'max']),
            Aggregate('from_compliance', ['mean', 'min', 'max']),
        ]

        aggregates.extend([Count(lambda i: i['closure'] == c, name='closure_%s' % c, prop=True) for c in CLOSURE_CODES])
       
        return aggregates

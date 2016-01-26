import os
import logging
from datetime import date

import pandas as pd
import numpy as np

from drain import util, aggregate, data
from drain.aggregate import Aggregate, Count, aggregate_counts, SpacetimeAggregator, Spacedeltas

day = np.timedelta64(1, 'D')
PERMIT_TYPES = ['electric_wiring', 'elevator_equipment', 'signs', 'new_construction', 'renovation_alteration', 'easy_permit_process', 'porch_construction', 'wrecking_demolition', 'scaffolding', 'reinstate_revoked_pmt', 'for_extension_of_pmt']

class PermitsAggregator(SpacetimeAggregator):
    def __init__(self, basedir, psql_dir=''):
        SpacetimeAggregator.__init__(self, 
                spacedeltas = {
                    'address':	Spacedeltas('address_id',['all','1y','3y']),
                    'building': Spacedeltas('building_id',['all','1y','3y']),
                    'complex': Spacedeltas('complex_id',['all','1y','3y']),
                    'block': Spacedeltas('census_block_id',['all','1y','3y']),
                    'tract':	Spacedeltas('census_tract_id',['all','1y','3y']),
                    'ward':	Spacedeltas('ward_id',['all','1y','3y'])
                },
                dates = [date(y,1,1) for y in xrange(2007,2015+1)],
                prefix = 'permits',
                basedir = basedir,
                date_col = 'issue_date')

        self.DEPENDENCIES = [os.path.join(psql_dir, 'aux/building_permits')]
        self.dtypes = np.float32

    def get_data(self, date):
        engine = util.create_engine()
        logging.info('Reading permits %s' % date)
        df = pd.read_sql("select * from aux.building_permits join output.addresses using (address) where issue_date < '%s'" % date, engine, parse_dates=['issue_date'])
  
        return df

    def get_aggregates(self, date, data):
         aggregates = [Count('permit_type_%s' % p, prop=True) for p in PERMIT_TYPES]
         aggregates.append(Count())
         
         return aggregates

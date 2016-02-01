import os
import logging
from datetime import date

import pandas as pd
import numpy as np

from drain import util, aggregate, data
from drain.aggregate import Aggregate, Count, aggregate_counts, SpacetimeAggregator, Spacedeltas

day = np.timedelta64(1, 'D')
VIOLATION_KEYWORDS = ['water', 'paint', 'window', 'wall', 'porch']

class ViolationsAggregator(SpacetimeAggregator):
    def __init__(self, basedir, psql_dir=''):
        SpacetimeAggregator.__init__(self, 
                spacedeltas = { space:	Spacedeltas(index,deltas) for space,index in spaces.iteritems() },
                dates = [date(y,1,1) for y in xrange(2007,2015+1)],
                prefix = 'violations',
                basedir = basedir,
                date_col = 'violation_date')

        self.DEPENDENCIES = [os.path.join(psql_dir, 'input/building_violations')]
        self.dtypes = np.float32

    def get_data(self, date):
        engine = util.create_engine()
        logging.info('Reading violations %s' % date)
        df = pd.read_sql("select a.*, violation_date, lower(violation_description) as violation_description from input.building_violations join output.addresses a using (address) where violation_date < '%s'" % date, engine, parse_dates=['violation_date'])

        for keyword in VIOLATION_KEYWORDS:
            df['keyword_' + keyword] = (df.violation_description.str.find(keyword) > -1)
  
        return df

    def get_aggregates(self, date, data):
         # TODO: add violation status (no entry, complied, open) features
         # censor on violation status date!
         aggregates = [Count('keyword_%s' % k, prop=True) for k in VIOLATION_KEYWORDS]
         aggregates.append(Count())
         
         return aggregates

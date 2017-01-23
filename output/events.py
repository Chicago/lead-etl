import os
import logging
from datetime import date

import pandas as pd
import numpy as np

from drain import util, aggregate, data
from drain.step import Step
from drain.aggregate import Aggregate, Count
from drain.aggregation import SpacetimeAggregation
from drain.data import FromSQL, Merge

day = np.timedelta64(1, 'D')

# inspection event codes
event_codes = [
    'INSAR', 'INSAC', 'INSSA', 'REINS', 'CMPLY', 'ENVPH', 'CONFL',
    'SATTY', 'MAYOR', 'CONTC'
]

# most common combinations of event and res codes
# TODO: consider including less common but useful ones
# TODO: switch to Binarize step with min_freq!
event_res_codes = [
    'REINS_C', 'INSSA_C', 'INSAR_N', 'CMPLY_C', 'ENVPH_C', 'INSAR_P',
    'CONFL_C', 'INSAR_W', 'SATTY_C', 'INSAR_Z', 'INSAC_P', 'INSAC_N',
    'INSAC_V', 'INSAR_J', 'INSAR_O', 'INSAR_G', 'INSAC_G', 'INSAC_Z',
    'INSAC_W', 'INSSA_L', 'INSSA_M', 'INSAR_C', 'INSAC_J', 'INSAR_V',
    'INSAC_O', 'INSSA_R', 'INSSA_W', 'INSAC_T', 'CONFL_Q', 'INSAR_T',
    'INSAR_U', 'INSAC_C', 'CONTC_C', 'INSSA_D', 'INSAR_B', 'INSAC_U'
]
events_table = FromSQL("""
                select comp_date, event_code, res_code, addresses.*
                from stellar.event
                join aux.stellar_addresses on addr_id = id_number
                join output.addresses using (address_id)
                where class = 'I'
            """, tables=['stellar.event', 'aux.stellar_addresses', 'output.addresses'],
            parse_dates=['comp_date'])
events_table.target = True

class Events(Step):
    def __init__(self):
        Step.__init__(self, inputs = [events_table])

    def run(self, event):
        # concatenate event and res code, e.g. 'REINS_C'
        event['event_res_code'] = event.event_code + '_' + event.res_code
        # binarize event code and event res codes
        data.binarize(event, {'event_code': event_codes, 
                              'event_res_code': event_res_codes})

        return event

events = Events()
events.target = True

class EventsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, parallel=False):
        SpacetimeAggregation.__init__(self,
                inputs = [events],
                spacedeltas = spacedeltas,
                dates = dates,
                prefix = 'events',
                date_column = 'comp_date', 
                parallel=parallel)

    def get_aggregates(self, date, delta):
        return [
            Count(),
            Count(['event_code_' + e for e in event_codes], prop=True),
            Count(['event_res_code_' + e for e in event_res_codes], prop=True)
        ]

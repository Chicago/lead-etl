from drain.data import FromSQL
from drain.aggregate import Count
from drain.aggregation import SpacetimeAggregation

PERMIT_TYPES = ['electric_wiring', 'elevator_equipment', 'signs', 'new_construction', 'renovation_alteration', 'easy_permit_process', 'porch_construction', 'wrecking_demolition', 'scaffolding', 'reinstate_revoked_pmt', 'for_extension_of_pmt']

permits = FromSQL("""
    select * from aux.building_permits 
    join output.addresses using (address)
    """, parse_dates=['issue_date'], 
    tables=['aux.building_permits', 'output.addresses'])
permits.target = True

class PermitsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, parallel=False):
        SpacetimeAggregation.__init__(self, inputs=[permits],
                spacedeltas=spacedeltas, 
                dates=dates, prefix = 'permits', 
                date_column = 'issue_date', 
                parallel=parallel)

    def get_aggregates(self, date, data):
         aggregates = [Count('permit_type_%s' % p, prop=True) for p in PERMIT_TYPES]
         aggregates.append(Count())
         
         return aggregates

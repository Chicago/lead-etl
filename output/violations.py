from drain.data import FromSQL
from drain.aggregate import Count
from drain.aggregation import SpacetimeAggregation
from itertools import product

KEYWORDS = ['water', 'paint', 'window', 'wall', 'porch', 'chip', 'flak', 'peel']
STATUS = (['OPEN', 'COMPLIED', 'NO ENTRY'],
          ['open', 'complied', 'no_entry'])

KEYWORD_COLUMNS = str.join(', ', 
        ("violation_description ~* '{0}' "
         "or violation_inspector_comments ~* '{0}' AS {0}".format(k) 
            for k in KEYWORDS))

STATUS_COLUMNS = str.join(', ',
        ("violation_status = '{0}' AS {1}".format(*s) 
            for s in zip(*STATUS)))

violations = FromSQL("""
select a.*, violation_date, violation_status, 
    violation_status_date, %s, %s
from input.building_violations 
join output.addresses a using (address)
""" % (KEYWORD_COLUMNS, STATUS_COLUMNS), 
    parse_dates=['violation_date', 'violation_status_date'], 
    tables=['input.building_violations', 'output.addresses'],
    target=True)

class ViolationsAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self, 
                spacedeltas=spacedeltas, dates=dates, 
                prefix = 'violations', date_column = 'violation_date',
                censor_columns = {'violation_status_date': ['violation_status']}, **kwargs)

        if not self.parallel:
            self.inputs = [violations]

    def get_aggregates(self, date, data):
        aggregates = [
            Count(),
            Count(KEYWORDS, prop=True),
            Count(STATUS[1], prop=True),
            Count([lambda v,k=k,s=s: v[k] & v[s]
                    for k,s in product(KEYWORDS, STATUS[1])], prop=True,
                    name=['%s_%s' % p for p in product(KEYWORDS, STATUS[1])]
                 )
        ]
        
        return aggregates

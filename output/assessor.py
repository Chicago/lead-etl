from drain.aggregation import SimpleAggregation
from drain.aggregate import Count, Aggregate, Proportion, Fraction
from drain.data import FromSQL

import numpy as np

CLASSES = ['residential', 'incentive', 'multifamily', 'industrial', 'commercial', 'brownfield', 'nonprofit']

class AssessorAggregation(SimpleAggregation):
    def __init__(self, indexes, **kwargs):
        SimpleAggregation.__init__(self, indexes=indexes, prefix='assessor', **kwargs)
        if not self.parallel:
            self.inputs = [FromSQL(query="select * from aux.assessor "
                "join output.addresses using (address)",
                tables=['aux.assessor', 'output.addresses'], target=True)]

    @property
    def aggregates(self):
        return [
            Count(),
            Aggregate('count', 'mean', 'assessents'),
            Aggregate('land_value', 'sum'),
            Aggregate(['min_age', 'max_age'], ['min', 'mean', 'max']),

            # residential total value and average value
            Fraction(
                Aggregate(lambda a: a.total_value.where(a.residential),
                          'sum', 'residential_total_value', fname=False),
                Aggregate(lambda a: a.apartments.where(a.residential).replace(0,1),
                          'sum', name='residential_units', fname=False),
                include_numerator=True, include_denominator=True
            ),

            # property total value and average value
            Fraction(
                Aggregate('total_value', 'sum', fname=False),
                Aggregate(lambda a: a.apartments.replace(0,1), 'sum', name='units', fname=False),
                include_numerator=True, include_denominator=True
            ),

            Aggregate('apartments', 'mean'),
            Aggregate('rooms', 'sum'),
            Aggregate('beds', 'sum'),
            Aggregate('baths', 'sum'),

            Proportion(lambda a: a.taxpayer_address == a.address, 'owner_occupied'),
            Proportion([lambda a, c=c: a[c] > 0 for c in CLASSES],
                    name=CLASSES)
        ]


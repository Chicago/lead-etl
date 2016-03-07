from drain.aggregation import SimpleAggregation
from drain.aggregate import Count, Aggregate, Proportion, Fraction

import numpy as np

CONDITIONS = ['condition_major', 'condition_minor', 
        'condition_uninhabitable', 'condition_sound']

class BuildingsAggregation(SimpleAggregation):
    def __init__(self, indexes, **kwargs):
        SimpleAggregation.__init__(self, indexes=indexes, prefix='buildings', **kwargs)

    @property
    def aggregates(self):
        return [
            Count(),
            Aggregate('area', 'sum'),
            Aggregate('years_built', [
                    lambda y: np.nanmedian(np.concatenate(y.values)),
                    lambda y: np.nanmean(np.concatenate(y.values)),
                    lambda y: np.nanmin(np.concatenate(y.values)),
                    lambda y: np.nanmax(np.concatenate(y.values)),
                ], fname = ['median', 'mean', 'min', 'max']),
            Aggregate('address_count', 'sum'),
            # average proportion of sound building condition
            Proportion(['%s_prop' % c for c in CONDITIONS],
                    parent ='condition_not_null',
                    name = CONDITIONS),
            Aggregate([lambda p: p['%s_prop' % c] > 0
                        for c in CONDITIONS],
                    'any',
                    name = CONDITIONS),
            Aggregate('stories', 'mean'),
            Aggregate('units', 'sum'),
            Proportion('pre1978_prop', 
                    parent=lambda i: i.pre1978_prop.notnull()),
        ]

CLASSES = ['residential', 'incentive', 'multifamily', 'industrial', 'commercial', 'brownfield', 'nonprofit']

class AssessorAggregation(SimpleAggregation):
    def __init__(self, indexes, **kwargs):
        SimpleAggregation.__init__(self, indexes=indexes, prefix='assessor', **kwargs)

    @property
    def aggregates(self):
        return [
            Aggregate('count', 'mean'),
            Aggregate('land_value', 'sum'),
            Aggregate('age', ['min', 'mean', 'max']),
            Fraction(Aggregate('total_value', 'sum', fname=False), 
                    Aggregate(lambda a: a.apartments.replace(0,1), 'sum', name='units', fname=False), 
                    include_numerator=True, include_denominator=True),
            Aggregate('rooms', 'sum'),
            Aggregate('beds', 'sum'),
            Aggregate('baths', 'sum'),
            Aggregate('building_area', 'sum'),
            Aggregate('land_area', 'sum'),

            Proportion(lambda a: a.owner_occupied > 0, 'owner_occupied'),
            Proportion([lambda a, c=c: a[c] > 0 for c in CLASSES],
                    name=CLASSES)
        ]

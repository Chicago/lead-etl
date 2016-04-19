from drain.aggregation import SimpleAggregation
from drain.aggregate import Count, Aggregate, Proportion, Fraction
from drain.data import FromSQL

import numpy as np

CONDITIONS = ['condition_major', 'condition_minor', 
        'condition_uninhabitable', 'condition_sound']

class BuildingsAggregation(SimpleAggregation):
    def __init__(self, indexes, **kwargs):
        SimpleAggregation.__init__(self, indexes=indexes, prefix='buildings', **kwargs)
        if not self.parallel:
            self.inputs = [FromSQL(query="select * from aux.buildings "
                "join (select distinct on (building_id) * "
                       "from output.addresses order by building_id, address_id) a "
                "using (building_id)",
                tables=['aux.buildings', 'output.addresses'], target=True)]

    @property
    def aggregates(self):
        return [
            Count(),
            Aggregate('area', 'sum'),
            Aggregate(lambda b: b.area * b.stories, 'mean', 'volume'),
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
            Proportion('pre1978_prop', parent=lambda i: i.pre1978_prop.notnull()),
        ]

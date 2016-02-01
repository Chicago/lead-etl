from drain.aggregation import SimpleAggregation
from drain.aggregate import Count, Aggregate, Proportion
from drain.data import FromSQL

import numpy as np

class BuildingsAggregation(SimpleAggregation):
    @property
    def aggregates(self):
        return [
            Count(),
            Aggregate('area', 'sum'),
            Aggregate('years_built', [
                    lambda y: np.nanmedian(np.concatenate(y.values)),
                    lambda y: np.nanmin(np.concatenate(y.values)),
                    lambda y: np.nanmax(np.concatenate(y.values)),
                ], function_names = ['median', 'min', 'max']),
            Aggregate('address_count', 'sum'),
            # average proportion of sound building condition
            Proportion('condition_sound_prop', parent='condition_not_null'),
            Proportion('condition_major_prop', parent='condition_not_null'),
            Proportion('condition_minor_prop', parent='condition_not_null'),
            Proportion('condition_uninhabitable_prop', parent='condition_not_null'),
            Aggregate('stories', 'mean'),
            Aggregate('units', 'sum'),
            Proportion('pre_1978', parent=lambda i: i.pre_1978.notnull()),
        ]

class AssessorAggregation(SimpleAggregation):
    @property
    def aggregates(self):
        return [
            Aggregate('count', 'mean'),
            Aggregate('land_value', 'sum'),
            Aggregate('total_value', 'sum'),
            Aggregate('age', ['min', 'mean', 'max']),
            Aggregate('apartments', 'sum'),
            Aggregate('rooms', 'sum'),
            Aggregate('beds', 'sum'),
            Aggregate('baths', 'sum'),
            Aggregate('building_area', 'sum'),
            Aggregate('land_area', 'sum'),

            Proportion('residential', parent='count'),
            Proportion('incentive', parent='count'),
            Proportion('multifamily', parent='count'),
            Proportion('industrial', parent='count'),
            Proportion('commercial', parent='count'),
            Proportion('brownfield', parent='count'),
            Proportion('nonprofit', parent='count'),
        ]

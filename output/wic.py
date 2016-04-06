import os
import logging

import pandas as pd
import numpy as np

from drain import util, aggregate, data
from drain.aggregate import Aggregate, Count, aggregate_counts, days
from drain.aggregation import SpacetimeAggregation
from drain.data import FromSQL
from drain.util import list_filter_none, union

class EnrollAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
                spacedeltas = spacedeltas,
                dates = dates,
                prefix = 'wicenroll',
                date_column = 'register_d', **kwargs)

        if not self.parallel:
            self.inputs = [FromSQL(query="""
with enroll as (
SELECT kid_id, p.* 
FROM cornerstone.partenrl p join aux.kid_wics using (part_id_i)
UNION ALL
SELECT kid_id, p.*
FROM cornerstone.partenrl p join aux.kid_mothers on p.part_id_i = mothr_id_i)

select *, 
array_remove(array[lang_1_c, lang_2_c, lang_3_c], null) as language,
array_remove(array[pa_cde1_c, pa_cde2_c, pa_cde3_c, pa_cde4_c, pa_cde5_c], null) as assistance
from enroll 
""", parse_dates=['register_d', 'last_upd_d'], target=True)]

    def get_aggregates(self, date, delta):
        
        aggregates = [
            Aggregate(lambda e: e.med_risk_f == 'Y', 'any', 
                'medical_risk', fname=False),
            Aggregate('emplymnt_c', lambda e: set(list_filter_none(e)), 
                'employment_status', fname=False),
            Aggregate('occptn_c', lambda o: set(list_filter_none(o)), 
                'occupation', fname=False),
            Aggregate(['hsehld_n', 'hse_inc_a'], 'median', 
                ['household_size', 'household_income']),
            Aggregate('language', lambda ls: union(set(l) for l in ls),
                fname=False),
            Aggregate('assistance', lambda ls: union(set(l) for l in ls),
                fname=False),
            Aggregate('clinicid_i', lambda c: set(c), 'clinic', fname=False)
        ]

        return aggregates


class BirthAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
                spacedeltas = spacedeltas,
                dates = dates,
                prefix = 'wicbirth',
                date_column = 'date_of_birth', **kwargs)

        if not self.parallel:
            self.inputs = [FromSQL(target=True, query="""
SELECT *, 
apgar_n::int as apgar,
nullif(lgt_inch_n, 0) as length,
nullif(wgt_grm_n, 0) as weight,
nullif(headcirc_n, 0) as head_circumference,
array_remove(array[
        inf_cmp1_c, inf_cmp2_c, inf_cmp3_c, inf_cmp4_c, inf_cmp5_c
], null) as complication
FROM aux.kids
JOIN aux.kid_mothers USING (kid_id)
JOIN cornerstone.birth USING (part_id_i, mothr_id_i)
""", parse_dates=['date_of_birth'])
            ]

    def get_aggregates(self, date, delta):
        
        aggregates = [
            Aggregate('length', 'max', fname=False),
            Aggregate('weight', 'max', fname=False),
            Aggregate('head_circumference', 'max', fname=False),
            Aggregate('apgar', 'max', 'apgar_score', fname=False),
            Aggregate('brth_typ_c', lambda b: set(b), 'place_type', fname=False),
            Aggregate('inf_disp_c',lambda i: set(i), 'disposition', fname=False),
            Aggregate('complication', lambda cs: union(set(c) for c in cs), fname=False),
            Aggregate(lambda b: b.apors_f == 'Y', 'any', 'apors', fname=False),
            Aggregate(lambda b: b.icu_f == 'Y', 'any', 'icu', fname=False),
            Aggregate('clinicid_i', lambda c: set(c), 'clinic', fname=False)
        ]

        return aggregates

class PrenatalAggregation(SpacetimeAggregation):
    def __init__(self, spacedeltas, dates, **kwargs):
        SpacetimeAggregation.__init__(self,
                spacedeltas = spacedeltas,
                dates = dates,
                prefix = 'wicprenatal',
                date_column = 'visit_d', **kwargs)

        if not self.parallel:
            self.inputs = [FromSQL(target=True, query="""
SELECT kid_id, date_of_birth, p.*
FROM aux.kids
JOIN aux.kid_mothers USING (kid_id)
JOIN cornerstone.birth b USING (part_id_i, mothr_id_i)
JOIN cornerstone.prenatl p ON b.mothr_id_i = p.part_id_i
where date_of_birth - visit_d between -365 and 365
""", parse_dates=['date_of_birth', 'visit_d'])
            ]

    def get_aggregates(self, date, delta):

        aggregates = [
            Count(),
            Aggregate(days('visit_d', 'date_of_birth'), ['min', 'max'], 'visit'),
            Aggregate('serv_typ_c', lambda s: set(s), 'service', fname=False),
            Aggregate('preg_nbr_n', 'max', 'previous_pregnancies', fname=False),
            Aggregate('lv_brth_n', 'max', 'previous_births', fname=False),
            Aggregate('othr_trm_n', 'max', 'previous_terminations', fname=False),
            Aggregate(lambda p: p.smk3_mth_f == 'Y', 'any', 'smoked_3mo', fname=False),
            Aggregate('cig3_day_n', 'max', 'cigarettes_per_day', fname=False),
            Aggregate(lambda p: p.drk3_mth_f == 'Y', 'any', 'drank_3mo', fname=False),
            Aggregate('dr_dy_wk_n', 'max', 'days_drank_per_week', fname=False),
            Aggregate('drnk_day_n', 'max', 'drinks_per_day', fname=False),
            Aggregate('clinicid_i', lambda c: set(c), 'clinic', fname=False)
        ]

        return aggregates

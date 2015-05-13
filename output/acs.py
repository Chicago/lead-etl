#! /usr/bin/python

from lead.model import util
from lead.output.aggregate import aggregate
import pandas as pd

columns = {
    'race_pct_white':  {'numerator': 'race_count_white', 'denominator': 'race_count_total'},
    'race_pct_black':  {'numerator': 'race_count_black', 'denominator': 'race_count_total'},
    'race_pct_hispanic': {'numerator': 'hispanic_count_hispanic', 'denominator': 'race_count_total'},
    'race_pct_asian':  {'numerator': 'race_count_asian', 'denominator': 'race_count_total'},
    
    'edu_pct_9th':          {'numerator': 'edu_count_9th', 'denominator': 'edu_count_total'},
    'edu_pct_12th':         {'numerator': 'edu_count_12th', 'denominator': 'edu_count_total'},
    'edu_pct_hs':         {'numerator': 'edu_count_hs', 'denominator': 'edu_count_total'},
    'edu_pct_some_college': {'numerator': 'edu_count_some_college', 'denominator': 'edu_count_total'},
    'edu_pct_aa':      {'numerator': 'edu_count_associates', 'denominator': 'edu_count_total'},
    'edu_pct_ba':      {'numerator': 'edu_count_ba', 'denominator': 'edu_count_total'},
    'edu_pct_advanced':     {'numerator': 'edu_count_advanced', 'denominator': 'edu_count_total'},
    
    'health_pct_insured_employer': {'numerator': 'health_count_insured_employer', 'denominator': 'health_count_total'},
    'health_pct_insured_purchase': {'numerator': 'health_count_insured_purchase', 'denominator': 'health_count_total'},
    'health_pct_insured_medicaid': {'numerator': 'health_count_insured_medicaid', 'denominator': 'health_count_total'},
    'health_pct_insured_medicare': {'numerator': 'health_count_insured_medicare', 'denominator': 'health_count_total'},
    'health_pct_insured_veteran': {'numerator': 'health_count_insured_veteran', 'denominator': 'health_count_total'},
    'health_pct_insured_military': {'numerator': 'health_count_insured_military', 'denominator': 'health_count_total'},
    'health_pct_uninsured': {'numerator': 'health_count_uninsured', 'denominator': 'health_count_total'},
    'health_pct_insured': {'numerator': 'health_count_insured', 'denominator': 'health_count_total'},

    'tenure_pct_owner': {'numerator':'tenure_count_owner', 'denominator':'tenure_count_total'},
    'tenure_pct_renter': {'numerator':'tenure_count_renter', 'denominator':'tenure_count_total'},
}

engine = util.create_engine()
acs = pd.read_sql('select * from input.acs', engine)
aggregated = aggregate(acs, columns, index=['geoid','year'])
aggregated.reset_index(inplace=True)
aggregated.sort(['geoid','year'], ascending=True, inplace=True)

filled = aggregated.groupby('geoid').transform(lambda d: d.sort('year').fillna(method='backfill'))
filled['geoid'] = aggregated['geoid']
filled.to_sql(name='acs', schema='output', con=engine, if_exists='replace', index=False)

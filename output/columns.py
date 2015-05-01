acs = {
    'race_pct_white':  {'numerator': 'race_count_white', 'denominator': 'race_count_total'},
    'race_pct_black':  {'numerator': 'race_count_black', 'denominator': 'race_count_total'},
    'race_pct_latino': {'numerator': 'race_count_latino', 'denominator': 'race_count_total'},
    'race_pct_asian':  {'numerator': 'race_count_asian', 'denominator': 'race_count_total'},
    
    'edu_pct_9th':          {'numerator': 'edu_count_9th', 'denominator': 'edu_count_total'},
    'edu_pct_12th':         {'numerator': 'edu_count_12th', 'denominator': 'edu_count_total'},
    'edu_pct_some_college': {'numerator': 'edu_count_some_college', 'denominator': 'edu_count_total'},
    'edu_pct_college':      {'numerator': 'edu_count_college', 'denominator': 'edu_count_total'},
    'edu_pct_advanced':     {'numerator': 'edu_count_advanced', 'denominator': 'edu_count_total'},
    
    'families_pct_poverty': {'numerator': 'families_count_poverty', 'denominator': 'families_count_total'},
    
    
    'health_pct_uninsured': {'numerator': 'health_count_uninsured', 'denominator': 'health_count'},
    'health_pct_insured_public': {'numerator': 'health_count_insured_public', 'denominator': 'health_count'},
    'health_pct_insured_private': {'numerator': 'health_count_insured_private', 'denominator': 'health_count'},
    'health_pct_minors_uninsured': {'numerator': 'health_minors_count_uninsured', 'denominator': 'health_minors_count'},
    
    'housing_pct_vacant': {'numerator':'housing_count_vacant', 'denominator':'housing_count'},
    'housing_pct_owner': {'numerator':'housing_count_owner', 'denominator':'housing_count'},
    'housing_pct_renter': {'numerator':'housing_count_renter', 'denominator':'housing_count'},
}

building = {
    'count': {},
    'avg_year_built': {'numerator': 'year_built', 'func':'mean' },
    'pct_pre_1978': {'numerator': (lambda b: b.year_built <= 1978), 'denominator': (lambda b: ~b.year_built.isnull() )},
    'pct_sound': {'numerator': (lambda b: b.bldg_condi == 'SOUND'), 'denominator': (lambda b: ~b.bldg_condi.isnull() )},
    'pct_major': {'numerator': (lambda b: b.bldg_condi == 'NEEDS MAJOR REPAIR'), 'denominator': (lambda b: ~b.bldg_condi.isnull() )},
    'pct_minor': {'numerator': (lambda b: b.bldg_condi == 'NEEDS MINOR REPAIR'), 'denominator': (lambda b: ~b.bldg_condi.isnull() )},
    'pct_uninhabitable': {'numerator': (lambda b: b.bldg_condi == 'UNINHABITABLE'), 'denominator': (lambda b: ~b.bldg_condi.isnull() )},
    'avg_stories': {'numerator': 'stories', 'func': 'mean'},
    'avg_units': {'numerator': 'units', 'func': 'mean'},
    'pct_vacant': {'numerator': 'vacant', 'denominator': 1}
}

assessor = {
    'count': {},
    'pct_residential': {'numerator': 'residential', 'denominator': (lambda a: ~a.residential.isnull() )},
    'avg_residential_total_value': {'numerator': (lambda a: a.total_value.where(a.residential) ), 'func':'mean'},
    'avg_non_residential_total_value': {'numerator': (lambda a: a.total_value.where(~a.residential) ), 'func':'mean'},
    'avg_residential_age' : {'numerator': (lambda a: a.age.where(a.residential) ), 'func':'mean'},
    'avg_non_residential_age' : {'numerator': (lambda a: a.age.where(~a.residential) ), 'func':'mean'}
}
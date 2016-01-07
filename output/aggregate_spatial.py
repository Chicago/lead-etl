import aggregate as a
import columns
import pandas as pd
from lead.model import util

engine = util.create_engine()

buildings = pd.read_sql('select * from aux.buildings_summary b join aux.addresses a using(address)', engine)
assessor = pd.read_sql('select * from aux.assessor_summary b join aux.addresses a using(address)', engine)
acs = pd.read_sql('select geo_id2 as census_tract_id, * from aux.acs', engine)
wt = pd.read_sql('select * from aux.ward_tracts', engine)

for level in ['tracts', 'wards']:
    if level == 'wards':
        acs_level = wt.merge(acs, on='census_tract_id', how='left')
        index = 'ward_id'
        weight = acs_level['area']
    else:
        acs_level = acs
        index = 'census_tract_id'
        weight = None
    
    acs_ag = a.aggregate(acs_level, columns.acs, weight, index)
    buildings_ag = a.aggregate(buildings, columns.building, index=index)
    assessor_ag = a.aggregate(assessor, columns.assessor, index=index)
    
    acs_ag.columns = ['acs_' + c for c in acs_ag.columns]
    assessor_ag.columns = ['assessor_' + c for c in assessor_ag.columns]
    buildings_ag.columns = ['buildings_' + c for c in buildings_ag.columns]
     
    ag = acs_ag.join(assessor_ag, how='outer')
    ag = ag.join(buildings_ag, how='outer')
    
    # to_sql using wrong datatype when writing index as such. can specify dtype with pandas .15.2
    ag.reset_index(inplace=True)
    ag.to_sql(level, engine, if_exists='replace', schema='output', index=False)

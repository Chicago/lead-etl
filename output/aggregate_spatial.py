import aggregate as a
import columns
import pandas as pd
from lead.model import util

engine = util.create_engine()

buildings = pd.read_sql('select * from aux.buildings_summary b join aux.addresses a using(address)', engine)
assessor = pd.read_sql('select * from aux.assessor_summary b join aux.addresses a using(address)', engine)
wt = pd.read_sql('select * from aux.ward_tracts', engine)

for level,index in [('tracts', 'census_tract_id'), ('wards', 'ward_id')]:
    buildings_ag = a.aggregate(buildings, columns.building, index=index)
    assessor_ag = a.aggregate(assessor, columns.assessor, index=index)
    
    assessor_ag.columns = ['assessor_' + c for c in assessor_ag.columns]
    buildings_ag.columns = ['buildings_' + c for c in buildings_ag.columns]
     
    ag = assessor_ag.join(buildings_ag, how='outer')
    
    # to_sql using wrong datatype when writing index as such. can specify dtype with pandas .15.2
    ag.reset_index(inplace=True)
    ag.to_sql(level, engine, if_exists='replace', schema='output', index=False)

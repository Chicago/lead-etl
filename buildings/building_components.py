#! /usr/bin/python

import pandas as pd
import numpy as np
from drain import util
from lead.aux.dedupe import dedupe

engine = util.create_engine()
edges = pd.read_sql("""
    with addresses as (
        select a.id, oa.ogc_fid from buildings.addresses a join buildings.original_addresses oa using (address)
    ) 

    select a1.ogc_fid id1, a2.ogc_fid id2 from addresses a1 join addresses a2 using (id) where a1.ogc_fid < a2.ogc_fid;
    """, engine)

components = dedupe.get_components(edges)
deduped = dedupe.components_dict_to_df(components)

deduped.to_sql('building_components',con=engine, schema='buildings', if_exists='replace', index=False)
dedupe.insert_singletons('buildings.original_buildings', 'buildings.building_components', 'ogc_fid', engine)

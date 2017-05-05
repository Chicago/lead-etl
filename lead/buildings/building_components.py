#!/usr/bin/env python
import pandas as pd
import numpy as np
from drain import util, dedupe

engine = util.create_engine()
edges = pd.read_sql("""
    with addresses as (
        select a.id, oa.gid from buildings.addresses a join buildings.original_addresses oa using (address)
    )

    select a1.gid id1, a2.gid id2 from addresses a1 join addresses a2 using (id) where a1.gid < a2.gid;
    """, engine)

components = dedupe.get_components(edges)
deduped = dedupe.components_to_df(components)

deduped.to_sql('building_components', con=engine,
               schema='buildings', if_exists='replace', index=False)
dedupe.insert_singletons('buildings.original_buildings',
                         'buildings.building_components', 'gid', engine)

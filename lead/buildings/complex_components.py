import pandas as pd
import numpy as np
from drain import util, dedupe

engine = util.create_engine()
edges = pd.read_sql("""
    with buildings as (
        select bc.id1 id, oa.orig_bldg_ from buildings.building_components bc join buildings.original_buildings oa on bc.id2 = oa.gid
    )

    select b1.id id1, b2.id id2 from buildings b1 join buildings b2 using (orig_bldg_) where b1.id < b2.id;
    """, engine)

components = dedupe.get_components(edges)
deduped = dedupe.components_to_df(components)

deduped.to_sql('complex_components', con=engine,
               schema='buildings', if_exists='replace', index=False)
dedupe.insert_singletons('buildings.original_buildings',
                         'buildings.complex_components', 'gid', engine)

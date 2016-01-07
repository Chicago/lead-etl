import pandas as pd
import numpy as np
from lead.model import util
import sys

def follow(id1, edges, visited = None, weak=True):
    if visited == None: visited = set() 
    visited.add(id1)
    for row in edges[edges['id1'] == id1].values:
        if(row[1] not in visited):
            follow(row[1], edges, visited)
    
    if weak:
        for row in edges[edges['id2'] == id1].values:
            if(row[0] not in visited):
                follow(row[0], edges, visited)
            
    return visited

def get_components(vertices, edges):
    visited = set()
    components = {}

    for id1 in vertices.values[:,0]:
        if id1 not in visited:
            c = follow(id1, edges)
            visited.update(c)
            components[id1] = c
    
    return components

engine = util.create_engine()
vertices = pd.read_sql("select id1 as id from aux.kid_edges where initials='{initials}' UNION select id2 from aux.kid_edges where initials='{initials}';".format(initials=sys.argv[1]), engine)
edges = pd.read_sql("select * from aux.kid_edges where initials = '{}'".format(sys.argv[1]), engine)

components = get_components(vertices, edges)
deduped = np.empty((0,2), dtype=int)

for id1 in components:
    deduped = np.append(deduped, [[id1, id2] for id2 in components[id1]], axis=0)

deduped = pd.DataFrame(deduped, columns=['id1', 'id2'])
if len(deduped) > 0:
    print deduped.to_csv(index=False, header=False),

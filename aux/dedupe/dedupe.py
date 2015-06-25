import pandas as pd
import numpy as np

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

# if sparse (a lot of disconnected vertices) find those separately (faster) 
def get_components(edges, vertices=None):
    if vertices is None:
        vertices = pd.DataFrame({'id':pd.concat((edges['id1'], edges['id2'])).unique()})

    visited = set()
    components = {}
    
    for id1 in vertices.values[:,0]:
        if id1 not in visited:
            c = follow(id1, edges)
            visited.update(c)
            components[id1] = c
    
    return components

def components_dict_to_df(components):
    deduped = np.empty((0,2), dtype=int)

    for id1 in components:
        deduped = np.append(deduped, [[id1, id2] for id2 in components[id1]], axis=0)

    deduped = pd.DataFrame(deduped, columns=['id1', 'id2'])
    return deduped
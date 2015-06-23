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
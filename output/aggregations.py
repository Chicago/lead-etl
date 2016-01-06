indexes = ['address_id', 'building_id', 'complex_id', 'census_block_id', 'census_tract_id', 'ward_id', 'community_area_id']
levels = ['address', 'building', 'complex', 'block', 'tract', 'ward', 'community']

def level_index(level):
    return indexes[levels.index(level)]

def index_level(index):
    return levels[indexes.index(index)]

from lead.output.buildings import BuildingsAggregation, AssessorAggregation
from drain.data import FromSQL

indexes = {'address':'address_id','building': 'building_id',
          'complex':'complex_id', 'block':'census_block_id',
          'tract':'census_tract_id', 'ward':'ward_id'}

def buildings():
    buildings = FromSQL(query="select * from aux.buildings join output.addresses using (building_id)", target=True)
    return [BuildingsAggregation(indexes, inputs=[buildings], parallel=True, target=True)]

def assessor():
    assessor = FromSQL(query="select * from aux.assessor join output.addresses using (address)", target=True)
    return [AssessorAggregation(indexes, inputs=[assessor], parallel=True, target=True)]

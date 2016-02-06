from lead.output.buildings import BuildingsAggregation, AssessorAggregation
from lead.output.tests import TestsAggregation
from lead.output.permits import PermitsAggregation
from lead.output.violations import ViolationsAggregation
from lead.output.inspections import InspectionsAggregation

from drain.data import FromSQL
from drain import util
from datetime import date

indexes = {'address':'address_id','building': 'building_id',
          'complex':'complex_id', 'block':'census_block_id',
          'tract':'census_tract_id'}

deltas = {'address': ['1y', '2y', '5y', 'all'],
          'block': ['1y','2y','5y'],
          'tract': ['1y','2y','3y']}
spacedeltas = {index: (indexes[index], deltas[index]) for index in deltas}

dates = [date(y,1,1) for y in range(2007,2017)]

def buildings():
    buildings = FromSQL(query="select * from aux.buildings join output.addresses using (building_id)", target=True)
    return [BuildingsAggregation(
        {k:v for k,v in indexes.iteritems() if k != 'address'}, 
        inputs=[buildings], parallel=True, target=True)]

def assessor():
    assessor = FromSQL(query="select * from aux.assessor join output.addresses using (address)", target=True)
    return [AssessorAggregation(indexes, inputs=[assessor], parallel=True, target=True)]

def tests():
    return [TestsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def inspections():
    return [InspectionsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def permits():
    return [PermitsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def violations():
    return [ViolationsAggregation(spacedeltas=util.dict_subset(spacedeltas, ('address', 'block')), 
            dates=dates, target=True, parallel=True)]

def all():
    return buildings() + tests() + inspections() + assessor() + permits() + violations()

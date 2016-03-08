from lead.output.buildings import BuildingsAggregation, AssessorAggregation
from lead.output.tests import TestsAggregation
from lead.output.kids import KidsAggregation
from lead.output.permits import PermitsAggregation
from lead.output.violations import ViolationsAggregation
from lead.output.inspections import InspectionsAggregation
from lead.output.wic import EnrollAggregation, BirthAggregation, PrenatalAggregation

from drain.data import FromSQL
from drain import util
from datetime import date
from repoze.lru import lru_cache

indexes = {'address':'address_id','building': 'building_id',
          'complex':'complex_id', 'block':'census_block_id',
          'tract':'census_tract_id'}

deltas = {'address': ['1y', '2y', '5y', '10y', 'all'],
          'block': ['1y','2y','5y'],
          'tract': ['1y','2y','3y']}
spacedeltas = {index: (indexes[index], deltas[index]) for index in deltas}

def buildings():
    buildings = FromSQL(query="select * from aux.buildings "
            "join output.addresses using (building_id)", 
            tables=['aux.buildings', 'output.addresses'], target=True)

    return [BuildingsAggregation(
        {k:v for k,v in indexes.iteritems() if k != 'address'}, 
        inputs=[buildings], parallel=True, target=True)]

def assessor():
    assessor = FromSQL(query="select * from aux.assessor "
            "join output.addresses using (address)",
            tables=['aux.assessor', 'output.addresses'], target=True)

    return [AssessorAggregation(indexes, inputs=[assessor], parallel=True, target=True)]

def tests(dates):
    return [TestsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def kids(dates):
    return [KidsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def inspections(dates):
    return [InspectionsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def permits(dates):
    return [PermitsAggregation(spacedeltas=spacedeltas, dates=dates, target=True, parallel=True)]

def violations(dates):
    return [ViolationsAggregation(spacedeltas=util.dict_subset(spacedeltas, ('address', 'block')), 
            dates=dates, target=True, parallel=True)]

def wic_enroll(dates):
    return [EnrollAggregation(spacedeltas={'kid':('kid_id', ['all'])}, 
            dates=dates, target=True, parallel=True)]

def wic_birth(dates):
    return [BirthAggregation(spacedeltas={'kid':('kid_id', ['all'])}, 
            dates=dates, target=True, parallel=True)]

def wic_prenatal(dates):
    return [PrenatalAggregation(spacedeltas={'kid':('kid_id', ['all'])}, 
            dates=dates, target=True, parallel=True)]

@lru_cache(maxsize=1)
def all(dates):
    dates = list(dates)
    return (buildings() + tests(dates) + inspections(dates) + assessor() + permits(dates) + 
            violations(dates) + kids(dates) + 
            wic_enroll(dates) + wic_prenatal(dates) + wic_birth(dates))

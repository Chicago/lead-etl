from lead.output.buildings import BuildingsAggregation
from lead.output.assessor import AssessorAggregation
from lead.output.tests import TestsAggregation
from lead.output.kids import KidsAggregation
from lead.output.permits import PermitsAggregation
from lead.output.violations import ViolationsAggregation
from lead.output.investigations import InvestigationsAggregation
from lead.output.events import EventsAggregation
from lead.output.wic import EnrollAggregation, BirthAggregation, PrenatalAggregation

from drain import util, data
from datetime import date
import sys
from drain.util import lru_cache

DATES = (date(y,1,25) for y in range (2003, 2016))

indexes = {
    'kid':'kid_id', 
    'address':'address_id',
    'building': 'building_id', 
    'complex':'complex_id', 
    'block':'census_block_id',
    'tract':'census_tract_id',
}

deltas = {
    'address': ['1y', '2y', '5y', '10y', 'all'],
    'complex': ['1y', '2y', '5y', '10y', 'all'],
    'block': ['1y','2y','5y'],
    'tract': ['1y','2y','3y']
}

wic = {'kid': ['all']}

args = dict(
    buildings = ['building', 'complex', 'block', 'tract'],
    assessor = ['address', 'building', 'complex', 'block', 'tract'],
    tests = deltas,
    investigations = deltas,
    events = deltas,
    permits = deltas,
    kids = dict(kid=['all'], **deltas),
    violations = util.dict_subset(deltas, ('address', 'block')),
    wic_enroll = wic,
    wic_birth = wic,
    wic_prenatal = wic,
)

@lru_cache(maxsize=10)
def all_dict(dates=None, lag=None):
    dates = list(dates if dates is not None else DATES)
    delta = data.parse_delta(lag) if lag is not None else None

    aggs = {}

    for name, a in args.iteritems():
        cls = getattr(sys.modules[__name__], '%sAggregation' % name.split('_')[-1].title())
        if name in ('buildings', 'assessor'):
            aggs[name] = cls(indexes={n:indexes[n] for n in a}, parallel=True)
            for i in aggs[name].inputs: i.target=True
        else:
            spacedeltas = {n: (indexes[n], d) 
                    for n, d in a.iteritems()}
            dates_lagged = [d - delta for d in dates] if delta is not None and name.startswith('wic') else dates
            aggs[name] = cls(spacedeltas=spacedeltas, dates=dates_lagged, parallel=True)
            for i in aggs[name].inputs: i.target=True

    return aggs

def all():
    return all_dict().values()

#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os
from itertools import product

from lead.model.util import create_engine, count_unique, execute_sql, PgSQLDatabase,prefix_columns, join_years
from lead.output.aggregate import aggregate

from datetime import date

def censor_inspections(inspections, end_date, delta):
    max_date = inspections[['init_date', 'comply_date']].max(axis=1)
    min_date = inspections[['init_date', 'comply_date']].min(axis=1)

    if delta != -1:
        start_date = end_date - np.timedelta64(delta*365, 'D')
        inspections = inspections[ ((min_date < end_date) & (min_date >= start_date)) | ((max_date < end_date) & (max_date >= start_date))].copy()
    else:
        inspections = inspections[ (min_date < end_date) | (max_date < end_date) ].copy()
    
    inspections['comply_date'] = inspections.comply_date.where(inspections.comply_date < end_date)
    inspections['init_date'] = inspections.init_date.where(inspections.init_date < end_date)

    inspections['aggregation_end'] = end_date
    
    return inspections

def aggregate_inspections(inspections, levels):
    #res_columns = {'res_count': {'numerator': 'residential'}}
    #for index in levels:
    #    count = aggregate(self.tables['addresses'], res_columns, index=index)
    #    count.columns = [index + '_res_count']
    #    inspections = inspections.merge(count.reset_index(), how='left', on=index)

    for column in ['hazard_int','hazard_ext']:
        inspections[column].fillna(True, inplace=True)
        inspections[column] = inspections[column].astype(int)

    inspections['comply'] = inspections.comply_date.notnull()
    inspections['init'] = inspections.init_date.notnull()

    dt = (inspections['comply_date'] - inspections['init_date']).where(inspections['comply'])
    day = np.timedelta64(1, 'D')
    inspections['days_to_compliance'] = dt[dt.notnull()] / day

    INSPECTION_COLUMNS = {
        'count': {'numerator':1},
        'inspected': {'numerator':'init', 'func': np.max},
        'complied': {'numerator':'comply', 'func': np.max},
        #TODO: percent of all houses inspected, number/prop of *unique* compliances (by addr_id or by address_id)
        'hazard_int_count': {'numerator':lambda i: i['hazard_int'] & ~i['comply']},
        'hazard_ext_count': {'numerator':lambda i: i['hazard_ext']},
        'hazard_int_prop': {'numerator':'hazard_int', 'denominator':1},
        'hazard_ext_prop': {'numerator':'hazard_ext', 'denominator':1},
        'compliance_count': {'numerator': 'comply'},
        'compliance_prop': {'numerator': 'comply', 'denominator': 1},
        'avg_init_to_comply_days': {'numerator': 'days_to_compliance', 'func':'mean'},
        'days_since_last_init': {'numerator': lambda i: (i['aggregation_end'] - i['init_date']) / day, 'func': 'min'},
        'days_since_last_comply': {'numerator': lambda i: (i['aggregation_end'] - i['comply_date']) / day, 'func': 'min'},
    }

    r = []
    for level in levels:
        #INSPECTION_COLUMNS['pct_inspected'] = {'numerator': 1, 'denominator': level + '_res_count', 'denominator_func': np.max}
        df = aggregate(inspections, INSPECTION_COLUMNS, index=[level])
        df['days_since_last_init'] = pd.to_timedelta(df['days_since_last_init'], 'D').astype(int)
        df['days_since_last_comply'] = pd.to_timedelta(df['days_since_last_comply'], 'D').astype(int)
        df.reset_index(inplace=True)
        df['aggregation_level'] = level
        df.rename(columns={level:'aggregation_id'}, inplace=True)
        r.append(df)

    return pd.concat(r)


if __name__ == '__main__':
    engine = create_engine()
    db = PgSQLDatabase(engine)

    inspections = pd.read_sql('select * from output.inspections', engine)
    inspections['comply_date'] = pd.to_datetime(inspections['comply_date'])
    inspections['init_date'] = pd.to_datetime(inspections['init_date'])

    addresses = pd.read_pickle(sys.argv[2])
    inspections = inspections.merge(addresses, on='address_id')

    levels = ['address_id', 'building_id', 'complex_id', 'census_block_id', 'census_tract_id', 'ward_id']
    deltas = [-1, 1, 3]#, 5, 7, 9]
    end_dates = map(lambda y: np.datetime64(date(y,1,1)), range(2007, 2015))

    def aggregated_inspections():
        for delta,end_date in product(deltas, end_dates):
            print end_date, delta
            censored_inspections = censor_inspections(inspections, end_date, delta)
            df = aggregate_inspections(censored_inspections, levels)
            df['aggregation_end'] = end_date
            df['aggregation_delta']=delta
            yield df
    
    df = pd.concat(aggregated_inspections())
        
    r = db.to_sql(df, 'inspections_aggregated', if_exists='replace', schema='output', 
                  pk=['aggregation_end', 'aggregation_delta', 'aggregation_level', 'aggregation_id'], index=False)
    if r != 0:
        sys.exit(r)
        

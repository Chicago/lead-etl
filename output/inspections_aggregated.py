#!/usr/bin/python

import pandas as pd
import numpy as np
import sys
import os

from lead.model.util import create_engine, count_unique, execute_sql, PgSQLDatabase,prefix_columns, join_years
from lead.output.aggregate import aggregate

from datetime import date,timedelta

def aggregate_inspections(inspections, years, levels):
    #res_columns = {'res_count': {'numerator': 'residential'}}
    #for index in levels:
    #    count = aggregate(self.tables['addresses'], res_columns, index=index)
    #    count.columns = [index + '_res_count']
    #    inspections = inspections.merge(count.reset_index(), how='left', on=index)

    for column in ['hazard_int','hazard_ext']:
        inspections[column].fillna(True, inplace=True)
        inspections[column] = inspections[column].astype(int)

    inspections['year'] = inspections['init_date'].fillna(inspections['comply_date']).apply(lambda d:d.year)
    inspections = join_years(inspections, years)

    comply_not_null = inspections[inspections.comply_date.notnull()]
    inspections['comply'] = (comply_not_null['comply_date'].apply(lambda d: d.year) < comply_not_null.year)
    inspections['comply'] = inspections['comply'].fillna(False).astype('int')
    dt = (inspections['comply_date'] - inspections['init_date']).where(inspections['comply'])
    inspections['days_to_compliance'] = dt[dt.notnull()] / np.timedelta64(1, 'D')

    INSPECTION_COLUMNS = {
        'count': {'numerator':1},
        'inspected': {'numerator':1, 'func': np.max},
        #TODO: percent of all houses inspected, number/prop of *unique* compliances (by addr_id or by address_id)
        'hazard_int_count': {'numerator':lambda i: i['hazard_int'] & ~i['comply']},
        'hazard_ext_count': {'numerator':lambda i: i['hazard_ext']},
        'hazard_int_prop': {'numerator':'hazard_int', 'denominator':1},
        'hazard_ext_prop': {'numerator':'hazard_ext', 'denominator':1},
        'compliance_count': {'numerator': 'comply'},
        'compliance_prop': {'numerator': 'comply', 'denominator': 1},
        'avg_init_to_comply_days': {'numerator': 'days_to_compliance', 'func':'mean'},
    }

    r = []
    for level in levels:
        #INSPECTION_COLUMNS['pct_inspected'] = {'numerator': 1, 'denominator': level + '_res_count', 'denominator_func': np.max}
        df = aggregate(inspections, INSPECTION_COLUMNS, index=[level,'year'])
        df.reset_index(inplace=True)
        df['aggregation_level'] = level
        df.rename(columns={level:'aggregation_id', 'year':'aggregation_end'}, inplace=True)
        df['aggregation_end'] = df['aggregation_end'].apply(lambda d: date(d,1,1))
        r.append(df)

    return pd.concat(r)


if __name__ == '__main__':
    inspections = pd.read_pickle(sys.argv[1])
    addresses = pd.read_pickle(sys.argv[2])
    inspections = inspections.merge(addresses, on='address_id')

    engine = create_engine()
    db = PgSQLDatabase(engine)

    levels = ['address_id', 'building_id', 'complex_id', 'census_block_id', 'census_tract_id', 'ward_id']
    deltas = [-1]
    years = range(2007, 2015)

    df = aggregate_inspections(inspections, years, levels)
    df['aggregation_delta']=-1
        
    r = db.to_sql(df, 'inspections_aggregated', if_exists='replace', schema='output', 
                  pk=['aggregation_end, aggregation_level, aggregation_id'], index=False)
    if r != 0:
        sys.exit(r)
        

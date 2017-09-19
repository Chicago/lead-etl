import pandas as pd
import numpy as np
from drain import util
import sys

def read_acs(table, columns, engine, offsets={0:{}}, first_year=2009):
    years = range(first_year, 2015+1) # TODO: automatically detect most recent year
    select = """
        select geoid, {fields} from acs{year}_5yr.{table}
        where geoid ~ 'US1703'
    """
    column_names = ['geoid']
    column_names.extend(columns.keys())

    dfs = []
    for year in years:
        for i, attrs in offsets.iteritems():
            offset = [c + i for c in columns.values()]
            cols = map( (lambda x: "{0}{1:03d}".format(table, x)), offset)
            s = select.format(fields=str.join(',', cols), year=year, table=table)
            df = pd.read_sql(s, engine)
            df.columns = column_names
            for attr in attrs:
                df[attr] = attrs[attr]
            df['year'] = year
            dfs.append(df)
    df = pd.concat(dfs)

    return df
        
# simple sum-aggregation of columns starting with prefix over index
def aggregate(df, prefix, index):
    return df.groupby(index).agg({c: 'sum' for c in df.columns if c.startswith(prefix)})

if __name__ == "__main__":
    engine = util.create_engine()
    index = ['geoid','year']

    race_table='C02003'
    race_columns = {
        'race_count_total': 1,
        'race_count_white': 3,
        'race_count_black': 4,
        'race_count_asian': 6
    }
    race_agg = read_acs(race_table, race_columns, engine)
    race_agg.set_index(index, inplace=True)

    hispanic_table = 'B03003'
    hispanic_columns = {
        'race_count_hispanic': 3
    }
    hispanic_agg = read_acs(hispanic_table, hispanic_columns, engine)
    hispanic_agg.set_index(index, inplace=True)

    poverty_table = 'B17010'
    poverty_columns = {
        'family_count_total': 1,
        'family_count_poverty': 2
    }
    poverty_agg = read_acs(poverty_table, poverty_columns, engine)
    poverty_agg.set_index(index, inplace=True)

    edu_table = 'B15001'
    edu_columns = {
        'edu_count_total':3,
        'edu_count_9th': 4,
        'edu_count_12th': 5,
        'edu_count_hs': 6,
        'edu_count_some_college': 7,
        'edu_count_associates': 8,
        'edu_count_ba': 9,
        'edu_count_advanced': 10,
    }
    edu_offsets = {
        0: {'sex':'male', 'age':'18-24'},
        8: {'sex':'male', 'age':'25-34'},
        16: {'sex':'male', 'age':'34-44'},
        24: {'sex':'male', 'age':'45-64'},
        32: {'sex':'male', 'age':'65+'},

        41: {'sex':'female', 'age':'18-24'},
        49: {'sex':'female', 'age':'25-34'},
        57: {'sex':'female', 'age':'34-44'},
        65: {'sex':'female', 'age':'45-64'},
        73: {'sex':'female', 'age':'65+'},
    }

    edu = read_acs(edu_table, edu_columns, engine, edu_offsets)
    edu_agg = aggregate(edu, prefix='edu', index=index)

    # HEALTH INSURANCE
    health_table='B27001'
    health_columns={
        'health_count_total': 0,
        'health_count_insured':1,
        'health_count_uninsured':2
    }
    health_offsets = {
        3: {'sex':'male', 'age': '<6'},
        6: {'sex':'male', 'age': '6-17'},
        9: {'sex':'male', 'age': '18-24'},
        12: {'sex':'male', 'age': '25-34'},
        15: {'sex':'male', 'age': '35-44'},
        18: {'sex':'male', 'age': '45-54'},
        21: {'sex':'male', 'age': '55-64'},
        24: {'sex':'male', 'age': '65-74'},
        27: {'sex':'male', 'age': '74+'},
        31: {'sex':'female', 'age': '<6'},
        34: {'sex':'female', 'age': '6-17'},
        37: {'sex':'female', 'age': '18-24'},
        40: {'sex':'female', 'age': '25-34'},
        43: {'sex':'female', 'age': '35-44'},
        46: {'sex':'female', 'age': '45-54'},
        49: {'sex':'female', 'age': '55-64'},
        52: {'sex':'female', 'age': '65-74'},
        55: {'sex':'female', 'age': '74+'},
    }
    health = read_acs(health_table, health_columns, engine, health_offsets, 2012)
    health_agg = aggregate(health, prefix='health', index=index)

    insurance_offsets = {
        3: {'sex':'male', 'age':'<18'},
        6: {'sex':'male', 'age':'18-64'},
        9: {'sex':'male', 'age':'65+'},
        13: {'sex':'female', 'age':'<18'},
        16: {'sex':'female', 'age':'18-64'},
        19: {'sex':'female', 'age':'65+'},
    }
    insurances = ['employer', 'purchase', 'medicare', 'medicaid', 'military', 'veteran']
    insurance = pd.DataFrame(columns=['geoid', 'year', 'sex', 'age'])
    for i in range(len(insurances)):
        health_insurance_table = 'C2700' + str(4+i)
        health_insurance_columns={
            'health_count_insured_' + insurances[i]: 1,
        }

        df = read_acs(health_insurance_table, health_insurance_columns, engine, insurance_offsets, 2012)
        insurance = insurance.merge(df, on=['geoid', 'year', 'sex', 'age'], how='outer')

    insurance_agg = aggregate(insurance, prefix='health', index=index)

    # TENURE
    tenure_table='B25003'
    tenure_columns={
        'tenure_count_total': 1,
        'tenure_count_owner': 2,
        'tenure_count_renter': 3
    }

    tenure = read_acs(tenure_table, tenure_columns, engine)
    tenure_agg = aggregate(tenure, prefix='tenure', index=index)


    mother_marital_status_table='B13002'
    mother_marital_status_columns={
        'mother_marital_status_count_total':2,
        'mother_marital_status_count_married':3,
        'mother_marital_status_count_unmarried':7,
    }

    mother_marital_status = read_acs(mother_marital_status_table, mother_marital_status_columns, engine)
    mother_marital_status_agg = aggregate(mother_marital_status, prefix='mother_marital_status', index=index)

    mother_poverty_table='B13010'
    mother_poverty_columns={
        'mother_poverty_count_total':0,
        'mother_poverty_count_below_100_percent':1,
        'mother_poverty_count_100_199_percent':2,
        'mother_poverty_count_over_200_percent':3
    }
    mother_poverty_offsets={
        3: {'marital_status': 'married'},
        7: {'marital_status': 'unmarried'}
    }

    mother_poverty = read_acs(mother_poverty_table, mother_poverty_columns, engine, offsets=mother_poverty_offsets)
    mother_poverty_agg = aggregate(mother_poverty, prefix='mother_poverty', index=index)

    mother_labor_table='B13012'
    mother_labor_columns={
        'mother_labor_count_total':0,
        'mother_labor_count_in_labor_force':1,
        'mother_labor_count_not_in_labor_force':2,
    }
    mother_labor_offsets={
        3: {'marital_status': 'married'},
        6: {'marital_status': 'unmarried'}
    }

    mother_labor = read_acs(mother_labor_table, mother_labor_columns, engine, offsets=mother_labor_offsets)
    mother_labor_agg = aggregate(mother_labor, prefix='mother_labor', index=index)

    mother_education_table='B13014'
    mother_education_columns={
        'mother_education_count_total':0,
        'mother_education_count_less_than_hs':1,
        'mother_education_count_high_school':2,
        'mother_education_count_some_college':3,
        'mother_education_count_ba':4,
        'mother_education_count_grad':5,
    }
    mother_education_offsets={
        3: {'marital_status': 'married'},
        9: {'marital_status': 'unmarried'}
    }

    mother_education = read_acs(mother_education_table, mother_education_columns, engine, offsets=mother_education_offsets)
    mother_education_agg = aggregate(mother_education, prefix='mother_education', index=index)

    mother_assistance_table='B13015'
    mother_assistance_columns={
        'mother_assistance_count_total':0,
        'mother_assistance_count_assistance':1,
        'mother_assistance_count_no_assistance':2,
    }
    mother_assistance_offsets={
        3: {'marital_status': 'married'},
        6: {'marital_status': 'unmarried'}
    }

    mother_assistance = read_acs(mother_assistance_table, mother_assistance_columns, engine,
                                 offsets=mother_assistance_offsets, first_year=2010)
    mother_assistance_agg = aggregate(mother_assistance, prefix='mother_assistance', index=index)

    acs = tenure_agg.join([insurance_agg, health_agg, edu_agg, poverty_agg, 
                   race_agg, hispanic_agg, 
                   mother_marital_status_agg, mother_education_agg, mother_assistance_agg, 
                   mother_labor_agg, mother_poverty_agg], how='outer')
    acs.reset_index(inplace=True)
    acs['census_tract_id']=acs['geoid'].apply(lambda g: float(g[7:]))
    acs.drop('geoid', axis=1, inplace=True)
    acs.to_csv(sys.argv[1], index=False)

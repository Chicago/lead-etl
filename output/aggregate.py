import pandas as pd
import numpy as np

def aggregate(df, columns, weight=None, index=None):
    if index is not None:
        if isinstance(index, basestring):
            df2 = df[[index]].copy()
        else:
            df2 = df[index].copy()
    else:
        df2 = pd.DataFrame(index=df.index)  
    
    # generate numerators and denominators
    agg_dict = {}
    
    for column,agg in columns.iteritems():
        if 'numerator' in agg:
            numerator = __series(df, agg['numerator'])
        else:
            numerator = pd.Series(np.ones(len(df)), index=df.index)
        if weight is not None:
            numerator *= weight
        
        df2[column+'_numerator'] = numerator
        
        # default function is sum
        if 'func' not in agg:
            agg['func'] = 'sum'
        
        agg_dict[column+'_numerator'] = agg['func']
        if 'denominator' in agg:
            denominator = __series(df, agg['denominator'])
            if weight is not None:
                denominator *= weight
            df2[column+'_denominator'] = denominator
            agg_dict[column+'_denominator'] = agg['denominator_func'] if 'denominator_func' in agg else agg['func'] 
    
    # aggregate
    df3 = df2.groupby(index).agg(agg_dict) if index is not None else df2
    
    # collect and rename
    df4 = pd.DataFrame(index=df3.index)
    for column in columns:
        if 'denominator' in columns[column]:
            df4[column] = df3[column+'_numerator']/df3[column+'_denominator']
        else:
            df4[column] = df3[column+'_numerator']
    return df4

def __series(df, attr):
    if hasattr(attr, '__call__'):
        return attr(df)
    elif attr in df.columns:
        return df[attr]
    else:
        return attr


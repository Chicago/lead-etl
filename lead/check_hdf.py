import pandas as pd
import sys

filename = sys.argv[1]

df = pd.DataFrame()
df.to_hdf(filename, 'df')
df2 = pd.read_hdf(filename, 'df')

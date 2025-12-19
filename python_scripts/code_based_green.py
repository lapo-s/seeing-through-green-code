import pandas as pd
import os
import numpy as np

# IPC
ipc = pd.read_parquet('data/patstat_ipc.parquet')
ipc = ipc[~ipc['Code'].isna()]
ipc['Code'] = ipc['Code'].astype(str).str.replace(' ', '')
print(f'IPC inventions: {len(ipc):,}')

# CPC
cpc= pd.read_parquet('data/patstat_cpc.parquet')
cpc['Code'] = cpc['Code'].astype(str).str.replace(' ', '')
cpc = cpc[~cpc['Code'].isna()]
print(f'CPC inventions: {len(cpc):,}')

green_codes = pd.read_csv('data/green_codes.csv')

granted_ipc = ipc[['appln_id', 'Code']]
granted_cpc = cpc[['appln_id', 'Code']]

def select_y02_y04(df):
    return df[df['Code'].str.startswith(('Y02', 'Y04'))]

green_1 = granted_ipc.merge(green_codes, on = 'Code', how = 'inner')
green_2 = granted_cpc.merge(green_codes, on = 'Code', how = 'inner')
green_3 = select_y02_y04(granted_cpc)

green = pd.concat([green_1, green_2, green_3])
print(f'Before drop dup: {len(green):,}')
green.drop_duplicates(subset='appln_id', inplace=True)
print(f'AFTER drop dup: {len(green):,}')

green = green[['appln_id']]
green.to_parquet('data/GREEN_all.parquet', engine = 'pyarrow')
print(f'{len(green):,}')
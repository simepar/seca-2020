import pandas as pd

# 1 - Dados
df = pd.read_csv('sr_uniao_da_vitoria.csv', index_col='data', parse_dates=True)
src = df['h_m']
srq = df['q_m3s']

# 2 - Daily Threshold

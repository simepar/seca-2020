import pandas as pd
import datetime as dt
import numpy as np


# 1 - Coleta das vazoes
dados = pd.read_csv('sr_uniao_da_vitoria.csv', index_col='data', parse_dates=True)
dados = dados.asfreq('D')
df_q  = dados['q_m3s'].to_frame()


# 2 - Preenchimento de falhas
df_q.columns = ['q_m3s_orig']
df_q['q_m3s_corr'] = df_q['q_m3s_orig'].interpolate(method='spline', order=3)
df_q.to_excel('vazoes_uva.xlsx')


# 3 - Daily Threshold
tuplas_idx = list(zip(src.index.month, src.index.day))
df_percentis = pd.DataFrame()
for t in pd.date_range(dt.datetime(1900,1,1), dt.datetime(1900,12,31)):
    janela = pd.date_range(t - dt.timedelta(days=15), t + dt.timedelta(days=15))
    tuplas_janela = list(zip(janela.month, janela.day))
    idx_t = [ i in tuplas_janela for i in tuplas_idx ]
    Q95 = np.percentile(src.loc[idx_t].to_numpy(), 95)
    print(t.toordinal())


    idx.month
    idx.day

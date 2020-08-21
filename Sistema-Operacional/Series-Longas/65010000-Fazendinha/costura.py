import pandas as pd, numpy as np, matplotlib.pyplot as plt

# Serie do Aguas (convencional + telemetrica)
df1 = pd.read_csv('cotas_aguaspr.txt', sep=' ', header=None).rename(columns={1:'year',2:'month',3:'day'})
sr1 = df1.set_index(pd.to_datetime(df1[['year','month','day']]))[6].copy().rename('cota_cm')

# Serie do SNIRH (telemetrica)
df2 = pd.read_csv('telemetria_SNIRH.csv')
df2 = df2.set_index(pd.to_datetime(df2['id.horDataHora']))
df2 = df2.set_index(df2.index.tz_localize(None))
sr2 = df2['horNivelAdotado'].copy()
sr2 = sr2.resample('D', base=3).mean()

# Combinar series
def combinar(x1, x2):
    if np.isnan(x1) & np.isnan(x2):
        return np.nan
    else:
        if not np.isnan(x1):
            return x1
        else:
            return x2
sr = sr1.combine(sr2, combinar).rename('cota_cm')
sr = sr.asfreq('D')
sr.plot()
plt.show()
sr.to_csv('serie_longa.csv', header=True, index_label='data')

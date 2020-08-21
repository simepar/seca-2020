# Posto do Aguas; os dados chegam em tempo real atraves da API do SNIRH
# 1o momento - coletar niveis
# 2o momento - realizar a transformada em vazoes

import pandas as pd, numpy as np, matplotlib.pyplot as plt

# 1 - Serie do Aguas (convencional + telemetrica)
df1 = pd.read_csv('dados_aguas_65010000.txt', sep=' ', decimal=',', na_values='-', header=None).rename(columns={1:'year',2:'month',3:'day'})
df1 = df1.set_index(pd.to_datetime(df1[['year','month','day']]))[[6,7]].copy()
srh1 = df1[6]
srq1 = df1[7]

# 2 - Serie do SNIRH (telemetrica)
df2 = pd.read_csv('telemetria_SNIRH_65010000.csv')
df2 = df2.set_index(pd.to_datetime(df2['id.horDataHora']))
df2 = df2.set_index(df2.index.tz_localize(None))
srh2 = df2['horNivelAdotado'].copy()
srh2 = srh2.resample('D', base=3).mean()
srq2 = df2['horVazao'].copy()
srq2 = srq2.resample('D', base=3).mean()

# # 3 - Verificar continuidade na referencia das cotas
# srh1.plot(color='blue', label='Aguas')
# srh2.plot(color='red', label='SNIRH')
# plt.legend()
# plt.grid()
# plt.show()
# # Tem descontinuidades importantes! NAO COSTURAR POR ENQUANTO

# # 4 - Verificar vazoes
# srq1.plot(color='blue', label='Vazao Aguas')
# srq2.plot(color='red', label='Vazao SNIRH')
# plt.legend()
# plt.grid()
# plt.show()

# 4 - Combinar series de cotas
def combinar(x1, x2):
    if np.isnan(x1) & np.isnan(x2):
        return np.nan
    else:
        if not np.isnan(x1):
            return x1
        else:
            return x2
srh = srh1.combine(srh2, combinar).rename('cota_cm')
srh = srh.asfreq('D')

# Verificar serie combinada
srh1.plot(color='blue', label='Aguas')
srh2.plot(color='red', label='SNIRH')
srh.plot(color='black', label='costurada')
plt.legend()
plt.grid()
plt.show()

# 4 - Exportar serie combinada e TRUNCADA PARA DEPOIS DE 2012
srh = srh.truncate(before='2012-01-01')
srh = srh.round(2)
srh.to_csv('srh_65010000_2020_05_31.csv', header=True, index_label='data')

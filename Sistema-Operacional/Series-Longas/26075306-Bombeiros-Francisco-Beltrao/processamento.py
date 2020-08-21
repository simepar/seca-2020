# Posto do Aguas; os dados chegam em tempo real atraves da API do SNIRH
# 1o momento - coletar niveis
# 2o momento - realizar a transformada em vazoes

import pandas as pd, numpy as np, matplotlib.pyplot as plt

# # 1 - Serie do Aguas (convencional + telemetrica)
# df1 = pd.read_csv('dados_aguas_65021800.txt', sep=' ', decimal=',', na_values='-', header=None).rename(columns={1:'year',2:'month',3:'day'})
# df1 = df1.set_index(pd.to_datetime(df1[['year','month','day']]))[[6,7]].copy()
# srh1 = df1[6]
# srq1 = df1[7]

# 2 - Serie do Simepar
df2 = pd.read_csv('telemetria_Simepar_26075306.csv')
df2 = df2.set_index(pd.to_datetime(df2['datahora']))
df2 = df2.set_index(df2.index.tz_localize(None))
srh2 = df2['nivel_m'].copy()*100
srh2 = srh2.resample('D', base=3).mean()
# srq2 = df2['horVazao'].copy() NAO TEM VAZAO
# srq2 = srq2.resample('D', base=3).mean() NAO TEM VAZAO

# # 3 - Verificar continuidade na referencia das cotas
# srh1.plot(color='blue', label='Aguas')
# srh2.plot(color='red', label='SNIRH')
# plt.legend()
# plt.grid()
# plt.show()

# # # 4 - Verificar vazoes
# # srq1.plot(color='blue', label='Vazao Aguas')
# # srq2.plot(color='red', label='Vazao SNIRH')
# # plt.legend()
# # plt.grid()
# # plt.show()
# #
# # 4 - Combinar series de cotas
# def combinar(x1, x2):
#     if np.isnan(x1) & np.isnan(x2):
#         return np.nan
#     else:
#         if not np.isnan(x1):
#             return x1
#         else:
#             return x2
# srh = srh1.combine(srh2, combinar).rename('cota_cm')
# srh = srh.asfreq('D')
#
# # Verificar serie combinada
# srh1.plot(color='blue', label='Aguas')
# srh2.plot(color='red', label='SNIRH')
# srh.plot(color='black', label='costurada')
# plt.legend()
# plt.grid()
# plt.show()


# # Verificar serie do Simepar
srh2.plot(color='blue', label='Simepar')
plt.legend()
plt.grid()
plt.show()


# 4 - Exportar serie
srh = srh2
srh = srh.round(2)
srh.to_csv('srh_26075306.csv', header=True, index_label='data')

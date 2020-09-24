import pandas as pd, numpy as np, datetime as dt
import glob
import os

### PARTE II - POS-PROCESSAMENTO ###

## 1 - Abre a planilha contendo o vinculo codigo SIA <-> codigo do posto
MANANCIAIS_SANEPAR = pd.read_excel('MANANCIAIS_SANEPAR_v_ago_2020.xlsx', dtype={"Posto selecionado": str, 'SIA':int}, skiprows=4).set_index("SIA")

## 2 - Abre a planilha Excel do Alvim
xlsx_alvim = pd.read_excel("Entradas/Monitoramento_Mananciais_Criticos.xlsx", dtype={'SIA':int}).set_index("SIA")

## 3 - Junta as anomalias mensais de cota fluviometrica no mesto DataFrame (para uso interno)
idx = pd.to_datetime([])
ANC_mes = pd.DataFrame(index=idx)
arqs = glob.glob('Saidas/Dados-Postos/*')
for arq in arqs:
    arq=arq.replace('\\','/') 
    posto_codigo  = arq.split('/')[2].split('_')[0]
    sr_anomalia   = pd.read_excel(arq, index_col='data')['anomalia'].rename(posto_codigo)
    ANC_mes = pd.concat([ANC_mes, sr_anomalia], axis=1)

## 4 - Adiciona na planilha do alvim as informacoes de cota correspondentes
for SIA in xlsx_alvim.index:
    posto_vinculado = MANANCIAIS_SANEPAR.loc[SIA, 'Posto selecionado']
    if pd.isnull(posto_vinculado):
        continue
    else:
        datas = ANC_mes.iloc[-3:].index
        AN_3 = ANC_mes.iloc[-3][posto_vinculado]
        xlsx_alvim.loc[SIA,'AN_COTA_{:%Y%m}'.format(datas[-3])] = AN_3
        AN_2 = ANC_mes.iloc[-2][posto_vinculado]
        xlsx_alvim.loc[SIA,'AN_COTA_{:%Y%m}'.format(datas[-2])] = AN_2
        AN_1 = ANC_mes.iloc[-1][posto_vinculado]
        xlsx_alvim.loc[SIA,'AN_COTA_{:%Y%m%d}'.format(datas[-1])] = AN_1

## 5 - Exporta a planilha do alvim completada com as anomalias de cota
xlsx_alvim = xlsx_alvim.sort_index()
xlsx_alvim.to_excel('Saidas/Monitoramento - Mananciais Críticos.xlsx', index_label='SIA')
print('Planilha de Anomalias e SPIs nos Mananciais Críticos ok!')

## 5 - Salva TODOS os dados de TODOS os mananciais para elaboracao dos graficos: anomalias de precipitacao + anomalias de cota (mensais e diarias)
csv_alvim  = pd.read_csv('Entradas/Monitoramento_Todos_Mananciais.csv', sep=';', index_col='DATA', parse_dates=True)

falta = []

with pd.ExcelWriter('Saidas/Monitoramento - Todos os Mananciais.xlsx', datetime_format='yyyy-mm-dd', date_format='yyyy-mm-dd', engine='xlsxwriter') as writer:
    for SIA in MANANCIAIS_SANEPAR.index:
        try:
            # Coleta anomalias de precipitacao
            AN_PREC_MENSAL     = csv_alvim.loc[:,(f'{SIA}_AN_MENSAL')].rename('AN_PREC_MENSAL_%')
            AN_PREC_TRIMESTRAL = csv_alvim.loc[:,(f'{SIA}_AN_TRIMESTRAL')].rename('AN_PREC_TRIMESTRAL_%')
            AN_PREC_SEMESTRAL  = csv_alvim.loc[:,(f'{SIA}_AN_SEMESTRAL')].rename('AN_PREC_SEMESTRAL_%')
            AN_PREC = pd.concat([AN_PREC_MENSAL, AN_PREC_TRIMESTRAL, AN_PREC_SEMESTRAL], axis=1)
            # Tenta coletar as anomalias de cota fluviometrica
            posto_vinculado = MANANCIAIS_SANEPAR.loc[SIA, 'Posto selecionado']
            if pd.isnull(posto_vinculado):
                    AN_PREC.to_excel(writer, sheet_name='SIA{}_Mes'.format(SIA), header=True, index_label='DATA', na_rep='NaN', float_format='%.2f', freeze_panes=(1,1))
                    print('Dados do manancial SIA {} ok!'.format(SIA))
            else:
                arq = glob.glob('Saidas/Dados-Postos/{}_*'.format(posto_vinculado))[0]
                AN_COTA = pd.read_excel(arq, sheet_name='Mensal', index_col='data', parse_dates=True)['anomalia']
                AN_COTA = AN_COTA.rename('AN_COTA_%')
                AN_MES = pd.concat([AN_PREC, AN_COTA], axis=1)
                AN_DIA = pd.read_excel(arq, sheet_name='Diario', index_col='data', parse_dates=True)['anomalia']
                AN_DIA = AN_DIA.rename('AN_COTA_%')
                AN_MES.to_excel(writer, sheet_name='SIA{}_Mes'.format(SIA), header=True, index_label='DATA', na_rep='NaN', float_format='%.2f', freeze_panes=(1,1))
                AN_DIA.to_excel(writer, sheet_name='SIA{}_Dia'.format(SIA), header=True, index_label='DATA', na_rep='NaN', float_format='%.2f', freeze_panes=(1,1))
                print('Dados do manancial SIA {} ok!'.format(SIA))
        except:
            falta.append(SIA)
            continue
    writer.save()

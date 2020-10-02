import pandas as pd, numpy as np, datetime as dt
import glob
from dateutil.relativedelta import relativedelta
from f_coleta_op_banco_Simepar import f_coleta_op_banco_Simepar
from f_coleta_op_telemetria_SNIRH import f_coleta_op_telemetria_SNIRH


### Funcoes ###
def resampler_arlan(X):
    X = X.to_numpy()

    X = X[np.where(~pd.isnull(X))]
    if len(X) < 3:
        return np.nan
    else:
        q25 = np.quantile(X, 0.25)
        q75 = np.quantile(X, 0.75)
        IQ = q75 - q25
        IQ = max(IQ, 30)
        X = X[np.where( (X>(q25-1.5*IQ)) & (X<(q75+1.5*IQ)) )]
        if len(X) < 1:
            return np.nan
        else:
            return np.mean(X)


### PARTE I - PROCESSAMENTO E COLETA DAS SERIES TELEMETRICAS ###
## 1 - Obtem a datahora de disparo
# dhdisp = dt.datetime.now()
dhdisp = dt.datetime(2020,10,1,12) # tem que ser 1 dia depois do fechamento!

## 2 - Coleta o vinculo SIA do manancial <-> Codigo do posto telemetrico
MANANCIAIS_SANEPAR = pd.read_excel('MANANCIAIS_SANEPAR_v_ago_2020.xlsx', \
    skiprows = 4, \
    index_col='SIA', \
    dtype={'Posto selecionado':str, 'Tempo real':str, 'Nome do posto':str})

## 3 - Obtem os postos que devem ser processados, sem repeticao
postos = MANANCIAIS_SANEPAR[['Posto selecionado','Nome do posto','Tempo real']].copy() # Com repeticao
postos = postos.drop_duplicates(subset='Posto selecionado', keep='first')              # Unicos
postos = postos.dropna(subset=['Posto selecionado'])                                   # Sem NaNs
postos = postos.set_index(['Posto selecionado'])
## 4 - Processa a serie longa de cada posto, obtendo as referencias mensais de cota para o calculo das anomalias
for posto_codigo in postos.index:
    posto_nome = postos.loc[posto_codigo, 'Nome do posto']
    print('Coletando telemetria do posto "{}" - "{}"'.format(posto_nome, posto_codigo))
    posto_quem = postos.loc[posto_codigo, 'Tempo real']
    pasta = glob.glob('Series-Longas/{}-*'.format(posto_codigo))[0]
    srh_longa = pd.read_csv(pasta+'/srh_{}.csv'.format(posto_codigo), index_col='data', parse_dates=True)['cota_obs_cm']
    ref = srh_longa.groupby([srh_longa.index.month]).agg('mean')
    ref = ref.rename(posto_codigo)
    ## 5 - Coleta a telemetria da serie contendo 12 meses anteriores ao mes atual + dados do mes atual
    # Monta os limites do intervalo de coleta
    t_ini_BRT = dhdisp - relativedelta(years=+1)
    t_ini_BRT = dt.datetime(t_ini_BRT.year, t_ini_BRT.month, 1, 0, 0)
    t_fim_BRT = dt.datetime(dhdisp.year, dhdisp.month, dhdisp.day, 23, 59) - relativedelta(days=+1)
    # Passa os limites do intervalo de coleta para UTC
    t_ini_UTC = t_ini_BRT + dt.timedelta(hours=3)
    t_fim_UTC = t_fim_BRT + dt.timedelta(hours=3)
    # Executa a coleta do SNIRH ou do Simepar, a depender do orgao vinculado
    if posto_quem == 'snirh':
        srh_bruta = f_coleta_op_telemetria_SNIRH(t_ini_UTC, t_fim_UTC, posto_nome, posto_codigo)
    elif posto_quem == 'simepar':
        srh_bruta = f_coleta_op_banco_Simepar(t_ini_UTC, t_fim_UTC, posto_nome, posto_codigo) # Retorna na frequencia de 1hr
    else:
        print('\tDEU PAU NA CONSULTA DA TELEMETRIA!')
        continue
    # Traz a serie bruta para o horario BRT com timezone naive e trunca os registros do dia atual
    idx_UTC = pd.to_datetime(srh_bruta.index).tz_localize(None)
    idx_BRT = idx_UTC - dt.timedelta(hours=3)
    srh_bruta = pd.Series(index=idx_BRT, data=srh_bruta.to_numpy(), name='cota_obs_cm')
    srh_bruta = srh_bruta.truncate(before=t_ini_BRT, after=t_fim_BRT)
    ## 6 - Agrega a serie telemetrica para a resolucao diaria, removendo eventuais ruidos com a funcao 'resampler_arlan'
    srh_dia = srh_bruta.resample('D', closed='left', label='left').apply(resampler_arlan)
    idx_ideal = pd.date_range(t_ini_BRT, t_fim_BRT, freq='D')
    srh_dia = srh_dia.reindex(idx_ideal, fill_value=np.nan)
    ## 7 - Computa as anomalias diarias
    DF_dia = srh_dia.to_frame()
    DF_dia['cota_ref_cm'] = DF_dia.apply(lambda x: ref.loc[x.name.month], axis=1)
    DF_dia['anomalia'] = DF_dia.apply(lambda x: (x.cota_obs_cm - x.cota_ref_cm)/x.cota_ref_cm * 100 \
        if ~np.any(np.isnan([x.cota_obs_cm, x.cota_ref_cm])) else np.nan, axis=1)
    ## 8 - Computa as anomalias mensais
    srh_mes = srh_dia.resample('M').apply(lambda x: np.nan if len(x) == 0 else np.nanmean(x))
    ultimo_valor = srh_mes.iloc[-1:] # Usar a media mensal
    ultimo_dia = srh_dia.iloc[-1:]   # Usar a label do ultimo dia
    srh_mes = srh_mes.drop(ultimo_valor.index, axis=0)
    s_ultimo = pd.Series(index=ultimo_dia.index, data=ultimo_valor.values, name=ultimo_valor.name)
    srh_mes = srh_mes.append(s_ultimo)
    srh_mes = srh_mes.rename('cota_obs_cm')
    DF_mes = srh_mes.to_frame()
    DF_mes['cota_ref_cm'] = DF_mes.apply(lambda x: ref.loc[x.name.month], axis=1)
    DF_mes['anomalia'] = DF_mes.apply(lambda x: (x.cota_obs_cm - x.cota_ref_cm)/x.cota_ref_cm * 100 \
        if ~np.any(np.isnan([x.cota_obs_cm, x.cota_ref_cm])) else np.nan, axis=1)
    ## 9 - Exporta
    with pd.ExcelWriter('Saidas/Dados-Postos/{}_{}.xlsx'.format(posto_codigo, posto_nome), datetime_format='yyyy-mm-dd', date_format='yyyy-mm-dd', engine='xlsxwriter') as writer:
        DF_mes.to_excel(writer, sheet_name='Mensal', header=True, index_label='data', na_rep='NaN', float_format='%.2f', freeze_panes=(1,1))
        DF_dia.to_excel(writer, sheet_name='Diario', header=True, index_label='data', na_rep='NaN', float_format='%.2f', freeze_panes=(1,1))
        writer.save()
        print('\tTelemetria e anomalias processadas com sucesso!')

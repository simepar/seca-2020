import pandas as pd, numpy as np, datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar

### PARTE III - GERACAO DOS GRAFICOS ###
## 1 - Abre a planilha de vinculo para capturar o rio
MANANCIAIS_SANEPAR = pd.read_excel('MANANCIAIS_SANEPAR_v_ago_2020.xlsx', skiprows=4, index_col='SIA')
## 2 - Plota um .png para cada manancial
sns.set()
for SIA in MANANCIAIS_SANEPAR.index:
#for SIA in [19]:
    if SIA == 206:
        continue
    if SIA == 377:
        continue

    GG = MANANCIAIS_SANEPAR.loc[SIA, 'GG']
    GR = MANANCIAIS_SANEPAR.loc[SIA, 'GR']
    municipio = MANANCIAIS_SANEPAR.loc[SIA, 'Município']
    localidade = MANANCIAIS_SANEPAR.loc[SIA, 'Localidade']
    manancial = MANANCIAIS_SANEPAR.loc[SIA, 'Manancial']

    ## Chuva
    # Prepara a figura
    fig, axs = plt.subplots(2, sharex=True)
    titulo = 'Monitoramento de Anomalias\nMunicípio - {}, Localidade - {}\nManancial - {}, Código SIA - {}\nGerência Geral - {}, Gerência Regional - {}'.format(municipio, localidade, manancial, SIA, GG, GR)
    fig.suptitle(titulo, fontsize=18, fontweight='bold')
    fig.set_size_inches(14, 18) # pixels/meu
    # Coleta as anomalias
    #AN_MES = pd.read_excel('Saidas/Monitoramento - Todos os Mananciais.xlsx', sheet_name='SIA{}_Mes'.format(SIA), index_col='DATA')
    AN_MES = pd.read_excel('Saidas/Monitoramento - Todos os Mananciais.xlsx', sheet_name='SIA{}_Mes'.format(SIA))
    AN_MES.index=AN_MES['DATA'].fillna(dt.datetime(2020,9,30))
    AN_MES=AN_MES.fillna(0)
    AN_MES=AN_MES.groupby(AN_MES.index).sum()
    #AN_MES=AN_MES.drop('DATA',axis=1)
 
    # Plota
    axs[0].plot(AN_MES['AN_PREC_MENSAL_%']    ,'o-', label='Mensal', color='Red')
    axs[0].plot(AN_MES['AN_PREC_TRIMESTRAL_%'],'o-', label='Trimestral', color='Orange')
    axs[0].plot(AN_MES['AN_PREC_SEMESTRAL_%'] ,'o-', label='Semestral', color='Green')
    axs[0].axhline(y=0, color='Grey', linestyle='--')
    #    Realiza ajustes
    axs[0].set_title('Anomalias de Precipitação na Bacia do Manancial', fontsize=14, fontweight='bold')
    axs[0].legend(title='Acumulado', loc='upper right')
    xfmt = mdates.DateFormatter('%b-%y')
    axs[0].set_ylabel('Anomalia (%)', fontsize=12)#, fontsize=14)
    axs[0].xaxis.set_major_formatter(xfmt)
    axs[0].set_ylim(-110,+110)
    axs[0].set_yticks([-100, -90, -75, -50, 0, 50, 100])
    axs[0].tick_params(axis="x")#, labelsize=14)
    axs[0].tick_params(axis="y")#, labelsize=14)

    ## Nivel
    try:
        # Coleta as anomalias
        ANC_MES = AN_MES[['AN_COTA_%']]
        #ANC_MES['dias_mes'] = ANC_MES.apply(lambda x: calendar.monthrange(x.name.year, x.name.month)[1], axis=1)
        #ANC_MES['data_plotagem'] = ANC_MES.apply(lambda x: dt.datetime(x.name.year, x.name.month,int(x.dias_mes/2)), axis=1)
        ANC_DIA = pd.read_excel('Saidas/Monitoramento - Todos os Mananciais.xlsx', sheet_name='SIA{}_Dia'.format(SIA), index_col='DATA')
        rio = MANANCIAIS_SANEPAR.loc[SIA, 'Rio de referencia']
        # Plota
        axs[1].plot(ANC_DIA.index, ANC_DIA.values,'-', label='Diária', color='Black')
        axs[1].plot(ANC_MES,'o-', label='Mensal', color='Red')
        axs[1].axhline(y=0, color='Grey', linestyle='--')
        # Realiza ajustes
        axs[1].set_title('Anomalias de Cota Fluviométrica no {}'.format(rio), fontsize=14, fontweight='bold')
        axs[1].legend(title='Média', loc='upper right')
        axs[1].set_ylabel('Anomalia (%)', fontsize=12)
        axs[1].xaxis.set_major_formatter(xfmt)
        axs[1].set_ylim(-110,+110)
        axs[1].set_yticks([-100, -75, -50, -25, 0, 50, 100])
        axs[1].tick_params(axis="x")
        axs[1].tick_params(axis="y")
    except:
        print('Manancial sem anomalia de nivel!')

    # Por a marca d'agua
    texto = 'Fonte: IAT e Simepar'
    ini = AN_MES.index[0].strftime("%m/%Y")
    fim = AN_MES.index[-1].strftime("%m/%Y")
    dia = AN_MES.index[-1].strftime("%d")
    periodo = 'Observações:\n \
        - Período: {} a {} (no último mês foram considerados os dados até o dia {}, sendo a anomalia de precipitação referente ao total esperado neste mês).\n \
        - Para os mananciais em que não há informações de cota fluviométrica, não foi possível vincular um posto representativo. \n \
        - Fonte: IAT e Simepar, em atendimento ao Monitoramento Hidrometeorológico Emergencial do estado do Paraná - 2020.'.format(ini, fim, dia)
    # periodo =
    fig.text(0.15, 0.42, s=texto, fontsize=30, color='gray', alpha=0.5)
    fig.text(0.15, 0.84, s=texto, fontsize=30, color='gray', alpha=0.5)
    fig.text(0.05, 0.05, s=periodo)
    # Salvar
    plt.savefig('Saidas/Graficos/{}-{}-SIA-{}.png'.format(GG, GR, SIA), dpi=300)
    plt.close(fig)
    print('Grafico do SIA {} ok!'.format(SIA))

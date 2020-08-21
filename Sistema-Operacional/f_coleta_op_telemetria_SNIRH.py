import pandas as pd, json, requests


def f_coleta_op_telemetria_SNIRH(t_ini, t_fim, posto_nome, posto_codigo):
    # Leitura do arquivo de conversao do posto_codigo ANA em posto_codigo telemetrico
    arq_conversao = pd.read_excel('conversao_codigos.xlsx', dtype={'codigo_ana':str, 'codigo_telemetrico':str})
    conversao = arq_conversao.set_index(['codigo_ana'])['codigo_telemetrico']
    posto_codigo = conversao.loc[posto_codigo]
    # Inicio do algoritmo do Gabriel
    var=pd.date_range(start=t_ini,end=t_fim,freq='15D',closed=None).strftime('%Y-%m-%d').tolist()
    var.append(t_fim)
    t_inia=var[:-1]
    t_fimb=var[1:]
    i=0
    for inicio,fim in zip(t_inia,t_fimb):
        url=url=f'http://www.snirh.gov.br/hidroweb/rest/api/documento/gerarTelemetricas?codigosEstacoes={posto_codigo}&tipoArquivo=3&periodoInicial={inicio}&periodoFinal={fim}'
        site=requests.get(url).text
        if site=='':
            break
        texto=json.loads(site)
        if i==0:
            dados=pd.json_normalize(texto[0]['medicoes'])
            i=1
        else:
            dados=dados.append(pd.json_normalize(texto[0]['medicoes']),ignore_index=True)
    dados = dados.reindex(columns=['id.horEstacao','id.horDataHora','horQChuva','horChuva','horQNivelAdotado','horNivelAdotado','horQVazao','horVazao'])
    dados = dados.set_index('id.horDataHora')
    dados = dados.sort_index(ascending=True)
    # Captura a serie e remove duplicidade
    srh = dados['horNivelAdotado'].copy()
    srh.index.name = 'datahora'
    srh = srh.rename('cota_cm', axis=0)
    srh = srh.loc[~srh.index.duplicated(keep='first')]
    # Retorna a serie "bruta" - em UTC
    return srh

import pandas as pd, json, requests
import xmltodict, json

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
def f_coleta_op_telemetria_SNIRH2(t_ini, t_fim, posto_nome, posto_codigo):
    # Leitura do arquivo de conversao do posto_codigo ANA em posto_codigo telemetrico

    # Inicio do algoritmo do Gabriel
    url="http://telemetriaws1.ana.gov.br/ServiceANA.asmx?op=DadosHidrometeorologicosGerais"
    headers = {'content-type': 'text/xml'}
    body = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <DadosHidrometeorologicosGerais xmlns="http://MRCS/">
                      <codEstacao>{posto_codigo}</codEstacao>
                      <dataInicio>{t_ini}</dataInicio>
                      <dataFim>{t_fim}</dataFim>
                    </DadosHidrometeorologicosGerais>
                  </soap:Body>
                </soap:Envelope>"""
    response = requests.post(url,data=body,headers=headers)
    dicionario = xmltodict.parse(response.text)
    dados_json=json.loads(json.dumps(dicionario))['soap:Envelope']['soap:Body']['DadosHidrometeorologicosGeraisResponse']['DadosHidrometeorologicosGeraisResult']['diffgr:diffgram']['DocumentElement']['DadosHidrometereologicos']
    dados=pd.DataFrame(dados_json)
    dados=dados.iloc[::-1]
    dados.index=pd.to_datetime(dados['DataHora'])
    # Captura a serie e remove duplicidade
    srh = dados['NivelSensor'].astype(float).copy()
    srh.index.name = 'datahora'
    srh = srh.rename('cota_cm', axis=0)
    srh = srh.loc[~srh.index.duplicated(keep='first')]
    # Retorna a serie "bruta" - em UTC
    return srh
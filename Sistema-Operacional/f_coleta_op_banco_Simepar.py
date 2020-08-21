import pandas as pd, numpy as np, datetime as dt
import psycopg2, psycopg2.extras


def f_coleta_op_banco_Simepar(t_ini, t_fim, posto_nome, posto_codigo):
    # Monta o texto
    texto_psql = "select hordatahora, horleitura, horqualidade  \
                    from telemetria.horaria \
                    where hordatahora >= '{}' and hordatahora <= '{}' \
                    and horestacao in ({}) \
                    and horsensor in (18)".format(t_ini, t_fim, posto_codigo)
    # Execução da consulta no banco do Simepar
    conn = psycopg2.connect(dbname='clim', user='hidro', password='hidrologia', host='tornado', port='5432')
    consulta = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
    consulta.execute(texto_psql)
    consulta = consulta.fetchall()
    df = pd.DataFrame(consulta, columns=['hordatahora','horleitura','horqualidade']).set_index('hordatahora')
    df = df.sort_index(ascending=True)
    df.horqualidade = df.horqualidade.astype(int)
    df.horleitura = df.horleitura.astype(float)

    # !!! CQD do banco nao pode ser aproveitado pois estava reprovando os dados atuais !!!

    # Captura a serie e remove duplicidade
    srh = df['horleitura']
    srh.index.name = 'datahora'
    srh = srh.loc[~srh.index.duplicated(keep='first')]

    # Passa as cotas para cm
    srh = srh * 100
    srh = srh.rename('cota_cm', axis=0)

    # Retorna a serie "bruta" - sem o CQD do banco e em UTC
    return srh

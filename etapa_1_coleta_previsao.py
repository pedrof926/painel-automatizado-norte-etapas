# etapa_1_coleta_previsao.py

import pandas as pd
import requests
from datetime import datetime
import time

# Carregar lista de municípios da Região Norte
df_municipios = pd.read_excel("dados/codigos_mun_norte.xlsx")
lista_codigos = df_municipios["CD_MUN"].astype(str).tolist()

# Lista para armazenar os resultados
dados_previsao = []

print("📡 Coletando previsão do INMET para os municípios da Região Norte...")

for codigo, nome in zip(df_municipios["CD_MUN"], df_municipios["NM_MUN"]):
    url = f"https://apiprevmet3.inmet.gov.br/previsao/{codigo}"
    try:
        response = requests.get(url, verify=False, timeout=10)
        previsao_json = response.json()

        previsoes_dias = previsao_json[str(codigo)]["manha"]

        for data in previsoes_dias:
            try:
                dia_previsao = previsao_json[str(codigo)]["manha"][data]
                tmin = float(dia_previsao["temperatura"]["min"])
                tmax = float(dia_previsao["temperatura"]["max"])
                tmed = round((tmin + tmax) / 2, 1)

                dados_previsao.append({
                    "Municipio": nome,
                    "Data": datetime.strptime(data, "%d/%m/%Y"),
                    "Tmin": tmin,
                    "Tmax": tmax,
                    "Tmedia": tmed
                })
            except Exception as e:
                print(f"⚠️ Erro ao processar dados de {nome} ({codigo}) em {data}: {e}")
                continue

        time.sleep(0.5)  # evitar sobrecarga na API

    except Exception as e:
        print(f"❌ Falha ao coletar dados para {nome} ({codigo}): {e}")
        continue

# Criar DataFrame final
df_final = pd.DataFrame(dados_previsao)

# Salvar arquivo Excel
df_final.to_excel("previsao_tmed_norte.xlsx", index=False)
print("✅ Arquivo 'previsao_tmed_norte.xlsx' gerado com sucesso!")

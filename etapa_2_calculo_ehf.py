# etapa_2_calculo_ehf.py

import pandas as pd

# 📥 Carregar arquivos
df_prev = pd.read_excel("previsao_tmed_norte.xlsx")  # saída da Etapa 1
df_t3 = pd.read_excel("dados/tmed_3dias_municipios_451.xlsx")
df_t30 = pd.read_excel("dados/temperatura_30_dias_municipios_corrigido_completo.xlsx")
df_lim = pd.read_excel("dados/ehf_percentis_norte_painel.xlsx")

# 🧼 Garantir formatos corretos
df_prev["Data"] = pd.to_datetime(df_prev["Data"])
df_t30["Data"] = pd.to_datetime(df_t30["Data"]) if "Data" in df_t30.columns else df_t30

# 🔐 Unificar chaves por CD_MUN
resultados = []

print("🧮 Calculando EHF conforme fórmula oficial...")

for _, linha in df_prev.iterrows():
    nome_mun = linha["Municipio"]
    data = linha["Data"]
    tmed = linha["Tmedia"]
    tmax = linha["Tmax"]
    tmin = linha["Tmin"]

    try:
        # Encontrar código IBGE correspondente
        cod_mun = df_lim[df_lim["NM_MUN"] == nome_mun]["CD_MUN"].values[0]

        # Obter valores históricos e limiares
        t3 = df_t3.loc[df_t3["CD_MUN"] == cod_mun, "Tmedia_3dias"].values[0]
        t30 = df_t30.loc[df_t30["CD_MUN"] == cod_mun, "Tmedia_30dias"].values[0]
        t95 = df_lim.loc[df_lim["CD_MUN"] == cod_mun, "Tmedia_p95"].values[0]
        t99 = df_lim.loc[df_lim["CD_MUN"] == cod_mun, "Tmedia_p99"].values[0]

        # 📐 Calcular EHF conforme fórmula original
        ehi_sig = tmed - t95
        ehi_accl = tmed - t30
        ehf = round(max(0, ehi_sig) * max(1, ehi_accl), 2)

        # Classificação baseada na Tmédia prevista
        if tmed < t95:
            classificacao = "Normal"
        elif tmed >= t95 and tmed < t99:
            classificacao = "Severo"
        else:
            classificacao = "Extremo"

        resultados.append({
            "CD_MUN": cod_mun,
            "Municipio": nome_mun,
            "Data": data,
            "Tmin": tmin,
            "Tmax": tmax,
            "Tmedia": tmed,
            "EHF": ehf,
            "Classificacao": classificacao
        })

    except Exception as e:
        print(f"⚠️ Erro ao processar {nome_mun} ({data.date()}): {e}")
        continue

# 📤 Salvar resultado final
df_resultado = pd.DataFrame(resultados)
df_resultado.to_excel("classificacao_ehf_previsao.xlsx", index=False)
print("✅ Arquivo 'classificacao_ehf_previsao.xlsx' gerado com sucesso!")

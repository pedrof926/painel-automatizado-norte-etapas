# 🌡️ Painel de Calor Extremo e Vulnerabilidade - Região Norte

Este painel interativo exibe a previsão de calor extremo (EHF) e a vulnerabilidade socioeconômica (GeoSES) para os 450 municípios da Região Norte do Brasil.

## 🔧 Etapas Automatizadas
1. **Etapa 1 (5h):** Coleta da previsão de temperatura via API do INMET
2. **Etapa 2 (5h30):** Cálculo do EHF e classificação
3. **Etapa 3 (6h):** Painel interativo em Dash com mapa, gráficos e risco combinado

## 📦 Arquivos Necessários

Coloque estes arquivos na pasta `dados/` do projeto:

- `geoses_norte_.xlsx`
- `Municipios_Regiao_Norte_2024.geojson`

E o arquivo diário gerado pela Etapa 2:

- `classificacao_ehf_previsao.xlsx`

## ▶️ Executando

### Local
```bash
pip install -r requirements.txt
python painel_dash.py

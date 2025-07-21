import pandas as pd
import geopandas as gpd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import json

# === Carregar dados ===
print("🔄 Lendo arquivos...")
df_ehf = pd.read_excel("classificacao_ehf_previsao.xlsx")
df_geoses = pd.read_excel("dados/geoses_norte_.xlsx")
gdf = gpd.read_file("dados/Municipios_Regiao_Norte_2024.geojson")

# === Preparar dados ===
print("🧮 Processando dados...")
# Unir GeoSES com nomes
df_geoses["Vulnerabilidade"] = 1 - ((df_geoses["GeoSES"] + 1) / 2)

df_ehf = df_ehf.rename(columns={"Municipio": "NM_MUN"})
df = df_ehf.merge(df_geoses, on="NM_MUN", how="left")

# Converter classificação em score numérico
score_map = {"Normal": 0, "Severo": 1, "Extremo": 2}
df["Score_EHF"] = df["Classificacao"].map(score_map)
df["Risco_Combinado"] = df["Score_EHF"] * df["Vulnerabilidade"]

# Filtrar apenas datas únicas para seleção
datas_unicas = sorted(df["Data"].dt.date.unique())

# === Inicializar app Dash ===
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Painel de Calor Extremo e Vulnerabilidade - Região Norte", style={"textAlign": "center"}),

    html.Div([
        html.Label("Selecione a data:"),
        dcc.Dropdown(id="filtro-data",
                     options=[{"label": str(d), "value": str(d)} for d in datas_unicas],
                     value=str(datas_unicas[0])),

        html.Label("Selecione a camada a exibir:"),
        dcc.RadioItems(id="filtro-camada",
                       options=[
                           {"label": "Classificação do EHF", "value": "Classificacao"},
                           {"label": "Risco Combinado (EHF + GeoSES)", "value": "Risco_Combinado"}
                       ],
                       value="Classificacao",
                       labelStyle={"display": "block"})
    ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"}),

    dcc.Graph(id="mapa-calor", style={"height": "700px", "width": "100%"}),

    html.Div(id="detalhes-municipio", style={"padding": "20px"})
])

@app.callback(
    Output("mapa-calor", "figure"),
    Input("filtro-data", "value"),
    Input("filtro-camada", "value")
)
def atualizar_mapa(data_str, camada):
    data = pd.to_datetime(data_str)
    df_filtrado = df[df["Data"] == data]
    gdf_merged = gdf.merge(df_filtrado, on="NM_MUN", how="left")

    if camada == "Classificacao":
        color_discrete_map = {"Normal": "green", "Severo": "orange", "Extremo": "red"}
        fig = px.choropleth_mapbox(
            gdf_merged,
            geojson=json.loads(gdf_merged.to_json()),
            locations=gdf_merged.index,
            color="Classificacao",
            color_discrete_map=color_discrete_map,
            mapbox_style="carto-positron",
            center={"lat": -3.5, "lon": -60},
            zoom=4.2,
            hover_name="NM_MUN"
        )
    else:
        fig = px.choropleth_mapbox(
            gdf_merged,
            geojson=json.loads(gdf_merged.to_json()),
            locations=gdf_merged.index,
            color="Risco_Combinado",
            color_continuous_scale="RdPu",
            mapbox_style="carto-positron",
            center={"lat": -3.5, "lon": -60},
            zoom=4.2,
            hover_name="NM_MUN"
        )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

@app.callback(
    Output("detalhes-municipio", "children"),
    Input("mapa-calor", "clickData"),
    Input("filtro-data", "value")
)
def mostrar_detalhes(clickData, data_str):
    if clickData is None:
        return "Clique em um município no mapa para ver os detalhes."

    nome_mun = clickData["points"][0]["hovertext"]
    data_selecionada = pd.to_datetime(data_str)

    dados_mun = df[(df["NM_MUN"] == nome_mun)].sort_values("Data")
    dados_mun = dados_mun[["Data", "Tmin", "Tmax", "Tmedia", "Classificacao"]]

    geoses_val = df_geoses[df_geoses["NM_MUN"] == nome_mun]["GeoSES"].values[0]

    tabela = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in dados_mun.columns])),
        html.Tbody([
            html.Tr([html.Td(str(val)) for val in row]) for row in dados_mun.values
        ])
    ])

    return html.Div([
        html.H3(f"Município: {nome_mun}"),
        html.P(f"Índice GeoSES: {geoses_val:.3f}"),
        html.H4("Previsão para os próximos dias:"),
        tabela
    ])

if __name__ == "__main__":
    app.run_server(debug=True)

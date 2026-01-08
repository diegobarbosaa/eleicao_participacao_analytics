"""
Dashboard de Participação Eleitoral

Dashboard interativo com Streamlit para visualizar métricas de participação eleitoral
do TSE, focado na taxa de comparecimento. Usa dados reais da camada Silver.

Execução: streamlit run src/participacao_eleitoral/dashboard.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
import plotly.express as px  # type: ignore
import polars as pl
import py7zr
import requests
import streamlit as st

from participacao_eleitoral.silver.region_mapper import RegionMapper

# Configuração da página
st.set_page_config(
    page_title="Participação Eleitoral - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Scroll suave para melhorar UX com filtros
st.markdown("<style>html {scroll-behavior: smooth;}</style>", unsafe_allow_html=True)

# Define project root para resolver caminho correto dos dados
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "silver" / "comparecimento_abstencao"

# Pasta temp para dados extraídos
TEMP_DATA_PATH = PROJECT_ROOT / "temp_data"

# Mapeamento de UF para nome completo
UF_NOME_MAP = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


# Função para carregar dados reais da Silver layer
@st.cache_data
def carregar_dados_reais(
    anos_selecionados: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega e agrega dados reais da Silver layer.

    Args:
        anos_selecionados: Lista de anos eleitorais para carregar dados.

    Returns:
        Tupla com três DataFrames:
        - df_nacional: Dados nacionais agregados por ano
        - df_regional: Dados regionais agregados por ano e região
        - df_mapa: Dados para mapa agregados por ano e UF

    Raises:
        Nenhum erro é propagado - problemas são logados e DataFrames vazios retornados.
    """
    if not anos_selecionados:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Baixar e extrair dados da GitHub Release
    url = "https://github.com/diegobarbosaa/eleicao_participacao_analytics/releases/download/v1.0.0-data/silver_data.7z"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open("temp.7z", "wb") as f:
            f.write(response.content)
        with py7zr.SevenZipFile("temp.7z", "r") as archive:
            archive.extractall(TEMP_DATA_PATH)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao baixar/extrair dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Verificar se arquivos existem na pasta extraída
    paths = []
    for ano in anos_selecionados:
        caminho = (
            TEMP_DATA_PATH / "silver" / "comparecimento_abstencao" / f"year={ano}" / "data.parquet"
        )
        if not caminho.exists():
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Arquivo de dados não encontrado para {ano}: {caminho}")
            continue
        paths.append((ano, caminho))

    if not paths:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        # Scan all selected years with year column
        scans = [
            pl.scan_parquet(str(caminho)).with_columns(pl.lit(ano).alias("Ano"))
            for ano, caminho in paths
        ]
        df = pl.concat(scans, how="vertical")

        # Agregação nacional por ano
        nacional = (
            df.group_by("Ano")
            .agg(
                [
                    pl.col("QT_COMPARECIMENTO").sum().alias("comparecimento_total"),
                    pl.col("QT_ABSTENCAO").sum().alias("abstencao_total"),
                    pl.col("TAXA_COMPARECIMENTO_PCT").mean().alias("taxa_comparecimento"),
                ]
            )
            .collect()
        )

        # Agregação regional por ano e região
        # Agrupa por Ano e NOME_REGIAO para mostrar evolução regional
        regional = (
            df.group_by(["Ano", "NOME_REGIAO"])
            .agg(
                [
                    pl.col("QT_COMPARECIMENTO").sum().alias("comparecimento_total"),
                    pl.col("QT_ABSTENCAO").sum().alias("abstencao_total"),
                    pl.col("TAXA_COMPARECIMENTO_PCT").mean().alias("taxa_comparecimento"),
                ]
            )
            .collect()
        )

        # Dados para mapa por ano e UF (excluindo ZZ)
        mapa_df = df.filter(pl.col("SG_UF") != "ZZ")
        mapa = (
            mapa_df.group_by(["Ano", "SG_UF"])
            .agg(
                [
                    pl.col("TAXA_COMPARECIMENTO_PCT").mean().alias("taxa_comparecimento"),
                ]
            )
            .collect()
        )

        # Converter para Pandas
        df_nacional = nacional.to_pandas()
        df_regional = regional.to_pandas()
        df_mapa = mapa.to_pandas()

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao processar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Adicionar coluna região ao df_mapa para filtragem
    if not df_mapa.empty:
        df_mapa["regiao"] = df_mapa["SG_UF"].map(RegionMapper.get_regiao)

    return df_nacional, df_regional, df_mapa


# Função para carregar geojson do Brasil
@st.cache_data
def carregar_geojson() -> dict[str, Any] | None:
    """Carrega geojson dos estados brasileiros."""
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())
    except requests.RequestException as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Erro carregando geojson: {e}")
        return None


# Título principal
st.title("Dashboard de Participação Eleitoral")

st.markdown(
    """
Dashboard interativo para análise de participação eleitoral brasileira, focado na **taxa de comparecimento**.
Dados reais da camada Silver (2022 e 2024).
"""
)

# Sidebar para filtros
st.sidebar.header("Filtros")

Anos_disponiveis = [2014, 2016, 2018, 2020, 2022, 2024]
Anos_selecionados = st.sidebar.multiselect(
    "Anos Eleitorais",
    Anos_disponiveis,
    default=Anos_disponiveis,
)

regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul", "Exterior"]
regiao_selecionada = st.sidebar.multiselect(
    "Região",
    regioes,
    default=regioes,
)

# Carregar dados
data = carregar_dados_reais(Anos_selecionados)
df_nacional = data[0]
df_regional = data[1]
df_mapa = data[2]
geojson = carregar_geojson()

# Renomear colunas para nomes consistentes
if not df_regional.empty:
    df_regional.rename(columns={"NOME_REGIAO": "Região"}, inplace=True)
if not df_mapa.empty:
    df_mapa.rename(columns={"SG_UF": "Estado (UF)"}, inplace=True)

# Renomear colunas para nomes amigáveis
if not df_nacional.empty:
    df_nacional.rename(
        columns={
            "taxa_comparecimento": "Taxa de Comparecimento (%)",
            "comparecimento_total": "Total de Comparecimentos",
            "abstencao_total": "Total de Abstenções",
        },
        inplace=True,
    )
if not df_regional.empty:
    df_regional.rename(
        columns={
            "taxa_comparecimento": "Taxa de Comparecimento (%)",
            "comparecimento_total": "Total de Comparecimentos",
            "abstencao_total": "Total de Abstenções",
        },
        inplace=True,
    )
if not df_mapa.empty:
    df_mapa.rename(
        columns={
            "taxa_comparecimento": "Taxa de Comparecimento (%)",
        },
        inplace=True,
    )

    # Garantir que a coluna 'Ano' seja tipo int64
    if "Ano" in df_nacional.columns:
        df_nacional["Ano"] = df_nacional["Ano"].astype("int64")
    if "Ano" in df_regional.columns:
        df_regional["Ano"] = df_regional["Ano"].astype("int64")
    if "Ano" in df_mapa.columns:
        df_mapa["Ano"] = df_mapa["Ano"].astype("int64")

# Validação de dados
required_cols = {"Ano": df_nacional, "Região": df_regional, "Estado (UF)": df_mapa}
for col, df in required_cols.items():
    if df.empty:
        st.warning(f"DataFrame vazio para {col}. Verifique dados Silver.")
        continue
    if col not in df.columns:
        st.warning(
            f"Coluna '{col}' ausente em DataFrame. Colunas disponíveis: {df.columns.tolist()}"
        )
        continue

# Filtro adicional para mapa
map_year = (
    st.sidebar.selectbox("Ano para Mapa", Anos_selecionados, index=len(Anos_selecionados) - 1)
    if Anos_selecionados
    else None
)

# Filtrar dados por seleção
if df_nacional.empty:
    df_nacional_filtrado = pd.DataFrame()
else:
    mask_nacional = df_nacional["Ano"].isin(Anos_selecionados)
    df_nacional_filtrado = df_nacional[mask_nacional].copy()

if df_regional.empty:
    df_regional_filtrado = pd.DataFrame()
else:
    mask_regional = df_regional["Ano"].isin(Anos_selecionados)
    df_regional_filtrado = df_regional[mask_regional].copy()

# Filtrar por regiões selecionadas
if not df_regional_filtrado.empty:
    df_regional_filtrado = df_regional_filtrado[
        df_regional_filtrado["Região"].isin(regiao_selecionada)
    ]

if df_mapa.empty:
    df_mapa_filtrado = pd.DataFrame()
else:
    df_mapa_filtrado = df_mapa[df_mapa["Ano"] == map_year].copy() if map_year else pd.DataFrame()

# Filtrar mapa por regiões selecionadas
if not df_mapa_filtrado.empty:
    df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado["regiao"].isin(regiao_selecionada)]

# Resetar índice após filtro
if not df_nacional_filtrado.empty:
    df_nacional_filtrado.reset_index(drop=True, inplace=True)
if not df_regional_filtrado.empty:
    df_regional_filtrado.reset_index(drop=True, inplace=True)
if not df_mapa_filtrado.empty:
    df_mapa_filtrado.reset_index(drop=True, inplace=True)

# Agregar dados regionais por média
# Tabs
tab_nacional, tab_mapa, tab_regional, tab_detalhes = st.tabs(
    ["Visão Nacional", "Mapa Interativo", "Comparação Regional", "Dados Detalhados"]
)

with tab_nacional:
    if df_nacional_filtrado.empty:
        st.warning("Nenhum dado nacional disponível para os anos selecionados.")
    else:
        st.header("Métricas Nacionais")
        st.markdown(
            """
            **Explicação:** As métricas abaixo referem-se ao último Ano selecionado. A Taxa de Comparecimento representa a porcentagem de eleitores que compareceram às urnas em relação ao total apto a votar.
            """
        )

        # Para métricas, usar o último ano selecionado
        ano_para_metricas = max(Anos_selecionados) if Anos_selecionados else None
        df_metricas = pd.DataFrame()
        if ano_para_metricas:
            df_metricas = df_nacional_filtrado[
                df_nacional_filtrado["Ano"] == ano_para_metricas
            ].copy()

            if not df_metricas.empty:
                # KPIs
                try:
                    if isinstance(df_metricas, pd.DataFrame) and len(df_metricas) > 0:
                        taxa_atual = df_metricas["Taxa de Comparecimento (%)"].iloc[0]
                        comparecimento = df_metricas["Total de Comparecimentos"].iloc[0]
                        abstencao = df_metricas["Total de Abstenções"].iloc[0]
                    else:
                        taxa_atual = comparecimento = abstencao = 0
                except Exception:
                    taxa_atual = comparecimento = abstencao = 0

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Taxa de Comparecimento", f"{taxa_atual:.1f}%")
                with col2:
                    st.metric("Total Comparecimentos", f"{comparecimento:,.0f}")
                with col3:
                    st.metric("Total Abstenções", f"{abstencao:,.0f}")
                # Gráfico de tendência histórica
                st.subheader("Tendência Histórica da Taxa de Comparecimento")
                st.markdown(
                    """
                    **Explicação:** Este gráfico mostra a evolução da taxa nacional ao longo dos Anos selecionados.
                    """
                )
                # Ordenar por ano
                df_plotar = df_nacional_filtrado.sort_values("Ano")
                df_plotar["Ano"] = df_plotar["Ano"].astype(str)
                fig = px.line(
                    df_plotar,
                    x="Ano",
                    y="Taxa de Comparecimento (%)",
                    title="Tendência Histórica da Taxa de Comparecimento",
                )
                # Força eixo X como categoria para evitar interpolação decimal nos anos
                fig.update_xaxes(tickangle=0, type="category")
                fig.update_layout(
                    title_x=0.5,
                    xaxis_title="Ano",
                    yaxis_title="Taxa de Comparecimento (%)",
                )
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("Dados não disponíveis para os anos selecionados.")

with tab_mapa:
    if df_mapa_filtrado.empty:
        st.warning("Nenhum dado de mapa disponível para os filtros selecionados.")
    else:
        st.header("Mapa Interativo da Taxa de Comparecimento")
        st.markdown(
            """
            **Explicação:** O mapa mostra a taxa de comparecimento por estado brasileiro no Ano selecionado para mapa. Cores mais claras indicam taxas mais altas.

            **Como usar:** Selecione o ano na barra lateral para comparar diferentes eleições.
            """
        )

        st.info("💡 Mudanças em filtros podem ajustar a visualização da página.")

        if geojson:
            try:
                # Verificar se coluna existe
                if "Estado (UF)" not in df_mapa_filtrado.columns:
                    st.error(
                        f"Coluna 'Estado (UF)' não encontrada. Colunas: {df_mapa_filtrado.columns.tolist()}"
                    )
                    st.stop()

                # Adicionar nome completo do estado
                df_mapa_filtrado["Nome Estado"] = df_mapa_filtrado["Estado (UF)"].map(UF_NOME_MAP)

                fig = px.choropleth(
                    df_mapa_filtrado,
                    geojson=geojson,
                    locations="Estado (UF)",
                    featureidkey="properties.sigla",
                    color="Taxa de Comparecimento (%)",
                    hover_name="Nome Estado",
                    hover_data=["Taxa de Comparecimento (%)"],
                    color_continuous_scale="YlGnBu",
                    range_color=(
                        df_mapa_filtrado["Taxa de Comparecimento (%)"].min(),
                        df_mapa_filtrado["Taxa de Comparecimento (%)"].max(),
                    ),
                    labels={"Taxa de Comparecimento (%)": "Taxa (%)"},
                    title=f"Taxa de Comparecimento por Estado - {map_year}",
                )
                fig.update_geos(
                    fitbounds="locations",
                    visible=False,
                    projection_type="mercator",
                )
                fig.update_layout(
                    coloraxis_colorbar={
                        "title": "Taxa (%)",
                        "thicknessmode": "pixels",
                        "thickness": 20,
                        "lenmode": "pixels",
                        "len": 250,
                        "tickfont": {"size": 11},
                    },
                    margin={"l": 10, "r": 10, "t": 60, "b": 10},
                    title_x=0.5,
                    title_font={"size": 18},
                )
                st.plotly_chart(fig, width="stretch")
                st.info(
                    "ℹ️ Votos do exterior não são exibidos no mapa pois representam votações internacionais sem localização geográfica específica."
                )
            except Exception as e:
                st.error(f"Erro ao renderizar mapa: {e}")
        else:
            st.warning("Dados ou geojson não disponíveis para o ano selecionado.")

with tab_regional:
    if df_regional_filtrado.empty:
        st.warning("Nenhum dado regional disponível para os filtros selecionados.")
    else:
        st.header("Comparação por Região")
        st.markdown(
            """
            **Explicação:** Este gráfico mostra a taxa de comparecimento por região ao longo dos anos selecionados.

            **Como usar:** Observe a evolução da participação eleitoral por região.
            """
        )

        fig = px.line(
            df_regional_filtrado.sort_values(["Região", "Ano"]),
            x="Ano",
            y="Taxa de Comparecimento (%)",
            color="Região",
            title="Evolução Regional da Taxa de Comparecimento",
            markers=True,
        )
        fig.update_layout(
            title_x=0.5,
            xaxis_title="Ano",
            yaxis_title="Taxa de Comparecimento (%)",
        )
        st.plotly_chart(fig, width="stretch")

with tab_detalhes:
    if df_nacional_filtrado.empty and df_regional_filtrado.empty:
        st.warning("Nenhum dado detalhado disponível para os filtros selecionados.")
    else:
        st.header("Dados Detalhados")
        st.markdown("**Explicação:** Tabelas com os dados calculados para os anos selecionados.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Dados Nacionais")
            if not df_nacional_filtrado.empty:
                # Adicionar coluna Tipo para destacar Exterior
                df_nacional_display = df_nacional_filtrado.copy()
                df_nacional_display["Tipo"] = "Nacional"
                # Como df_nacional não tem NOME_REGIAO, assumimos que Exterior aparece em regional
                st.dataframe(df_nacional_display, width="stretch")

        with col2:
            st.subheader("Dados por Região")
            if not df_regional_filtrado.empty:
                # Adicionar coluna Tipo
                df_regional_display = df_regional_filtrado.copy()
                df_regional_display["Tipo"] = np.where(
                    df_regional_display["Região"] == "Exterior", "Internacional", "Nacional"
                )
                st.dataframe(df_regional_display, width="stretch")

# Footer
st.markdown("---")
st.caption(
    "Dashboard desenvolvido com Streamlit. Dados da camada Silver - TSE (Tribunal Superior Eleitoral)."
)
st.caption(f"Anos selecionados: {', '.join(map(str, Anos_selecionados))}")

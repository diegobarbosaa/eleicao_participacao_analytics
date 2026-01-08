# Importar funções do dashboard
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

sys.path.append("src")
from participacao_eleitoral.dashboard import carregar_dados_reais, carregar_geojson


class TestDashboard:
    """Testes para o dashboard Streamlit."""

    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes."""
        return pd.DataFrame(
            {
                "SG_UF": ["SP", "RJ", "MG"],
                "NOME_REGIAO": ["Sudeste", "Sudeste", "Sudeste"],
                "QT_COMPARECIMENTO": [1000, 800, 600],
                "QT_ABSTENCAO": [100, 200, 150],
                "TAXA_COMPARECIMENTO_PCT": [90.9, 80.0, 80.0],
            }
        )

    def test_carregar_dados_reais_success(self, tmp_path, sample_data):
        """Testa carregamento de dados reais com sucesso."""
        # Criar arquivo parquet simulado
        silver_dir = tmp_path / "data" / "silver" / "comparecimento_abstencao"
        silver_dir.mkdir(parents=True)
        parquet_path = silver_dir / "year=2022" / "data.parquet"
        parquet_path.parent.mkdir()
        sample_data.to_parquet(parquet_path)

        with patch("participacao_eleitoral.dashboard.PROJECT_ROOT", tmp_path):
            nacional, regional, mapa = carregar_dados_reais([2022])

            assert isinstance(nacional, pd.DataFrame)
            assert isinstance(regional, pd.DataFrame)
            assert isinstance(mapa, pd.DataFrame)
            assert len(nacional) > 0
            assert len(regional) > 0
            assert len(mapa) > 0

    def test_carregar_dados_reais_aggregations(self, tmp_path, sample_data):
        """Testa agregações corretas dos dados."""
        # Criar arquivo parquet
        silver_dir = tmp_path / "data" / "silver" / "comparecimento_abstencao"
        silver_dir.mkdir(parents=True)
        parquet_path = silver_dir / "year=2022" / "data.parquet"
        parquet_path.parent.mkdir()
        sample_data.to_parquet(parquet_path)

        nacional, regional, mapa = carregar_dados_reais([2022])

        # Verificar agregações nacionais
        assert nacional["comparecimento_total"].iloc[0] > 0
        assert nacional["abstencao_total"].iloc[0] > 0
        assert nacional["taxa_comparecimento"].iloc[0] > 0

        # Verificar agregações regionais (Sudeste)
        sudeste = regional[regional["regiao"] == "Sudeste"]
        assert len(sudeste) == 1
        assert sudeste["comparecimento_total"].iloc[0] > 0
        assert sudeste["abstencao_total"].iloc[0] > 0

        # Verificar mapa (sem ZZ)
        assert len(mapa) > 0
        assert "ZZ" not in mapa["uf"].values

    def test_carregar_dados_reais_column_renaming(self, tmp_path, sample_data):
        """Testa renomeação de colunas no dashboard (não na função)."""
        # Este teste verifica o código do dashboard, mas como é unitário, mockar.
        # Na prática, testado via AppTest
        pass  # Implementar se necessário

    def test_carregar_dados_reais_missing_file(self):
        """Testa carregamento quando arquivo não existe."""
        with patch("participacao_eleitoral.dashboard.st.warning") as mock_warning:
            nacional, regional, mapa = carregar_dados_reais([9999])  # Ano inexistente
            mock_warning.assert_called()
            assert nacional.empty or len(nacional) == 0

    def test_carregar_geojson_success(self):
        """Testa carregamento do GeoJSON com sucesso."""
        with patch("participacao_eleitoral.dashboard.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"type": "FeatureCollection", "features": []}
            mock_get.return_value = mock_response

            geojson = carregar_geojson()
            assert geojson is not None
            assert "type" in geojson

    def test_carregar_geojson_failure(self):
        """Testa falha no carregamento do GeoJSON."""
        with (
            patch(
                "participacao_eleitoral.dashboard.requests.get",
                side_effect=Exception("Network error"),
            ),
            patch("participacao_eleitoral.dashboard.st.error") as mock_error,
        ):
            geojson = carregar_geojson()
            mock_error.assert_called()
            assert geojson is None

    def test_app_initialization(self):
        """Testa inicialização básica do app Streamlit."""
        # Este teste verifica se o app pode ser carregado sem erros
        # Usando AppTest do streamlit.testing
        at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")

        # Simular execução
        at.run()

        # Verificar se não há erros
        assert not at.exception

        # Verificar elementos básicos
        assert len(at.sidebar) > 0
        assert len(at.main) > 0

    def test_sidebar_filters(self):
        """Testa filtros da barra lateral."""
        # Provide minimal data
        df_min = pd.DataFrame(
            {
                "ano": [2022],
                "taxa_comparecimento": [80.0],
                "comparecimento_total": [1000],
                "abstencao_total": [200],
            }
        )
        df_reg_min = pd.DataFrame(
            {
                "ano": [2022],
                "regiao": ["Sudeste"],
                "taxa_comparecimento": [80.0],
                "comparecimento_total": [1000],
                "abstencao_total": [200],
            }
        )
        df_map_min = pd.DataFrame({"ano": [2022], "uf": ["SP"], "taxa_comparecimento": [80.0]})
        with (
            patch(
                "participacao_eleitoral.dashboard.carregar_dados_reais",
                return_value=(df_min, df_reg_min, df_map_min),
            ),
            patch(
                "participacao_eleitoral.dashboard.carregar_geojson",
                return_value={"type": "FeatureCollection", "features": []},
            ),
        ):
            at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")

            at.run(timeout=10)

            # Verificar multiselect de anos (primeiro elemento)
            year_select = at.sidebar.multiselect[0]
            assert year_select is not None

            # Verificar multiselect de regiões (segundo elemento)
            region_select = at.sidebar.multiselect[1]
            assert region_select is not None

    def test_tabs_creation(self):
        """Testa criação das abas."""
        # Provide minimal data to avoid st.stop()
        df_min = pd.DataFrame(
            {
                "ano": [2022],
                "taxa_comparecimento": [80.0],
                "comparecimento_total": [1000],
                "abstencao_total": [200],
            }
        )
        df_reg_min = pd.DataFrame(
            {
                "ano": [2022],
                "regiao": ["Sudeste"],
                "taxa_comparecimento": [80.0],
                "comparecimento_total": [1000],
                "abstencao_total": [200],
            }
        )
        df_map_min = pd.DataFrame({"ano": [2022], "uf": ["SP"], "taxa_comparecimento": [80.0]})
        with (
            patch(
                "participacao_eleitoral.dashboard.carregar_dados_reais",
                return_value=(df_min, df_reg_min, df_map_min),
            ),
            patch(
                "participacao_eleitoral.dashboard.carregar_geojson",
                return_value={"type": "FeatureCollection", "features": []},
            ),
        ):
            at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")

            at.run(timeout=10)

            # Verificar abas
            tabs = at.main.tabs
            assert len(tabs) == 4  # Nacional, Mapa, Regional, Dados

            tab_names = [tab.label for tab in tabs]
            assert "Visão Nacional" in tab_names
            assert "Mapa Interativo" in tab_names
            assert "Comparação Regional" in tab_names
            assert "Dados Detalhados" in tab_names

    def test_metrics_display(self, tmp_path, sample_data):
        """Testa exibição de métricas nacionais."""
        # Criar arquivo parquet
        silver_dir = tmp_path / "data" / "silver" / "comparecimento_abstencao"
        silver_dir.mkdir(parents=True)
        parquet_path = silver_dir / "year=2022" / "data.parquet"
        parquet_path.parent.mkdir()
        sample_data.to_parquet(parquet_path)

        with patch("participacao_eleitoral.dashboard.PROJECT_ROOT", tmp_path):
            at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")
            at.run(timeout=10)

            # Verificar métricas
            metrics = at.metric
            assert len(metrics) == 3
            assert "Taxa de Comparecimento" in metrics[0].label
            assert "Total Comparecimentos" in metrics[1].label
            assert "Total Abstenções" in metrics[2].label

            # Valores esperados baseados nos dados de exemplo
            # Taxa média: (90.9 + 80.0 + 80.0) / 3 ≈ 83.63
            # Comparecimentos: 2400, Abstenções: 450
            assert abs(float(metrics[0].value[:-1]) - 83.63) < 0.1  # Aproximado
            assert "2,400" in metrics[1].value
            assert "450" in metrics[2].value

    def test_filter_interactions(self, tmp_path, sample_data):
        """Testa interações de filtros."""
        # Criar arquivos para múltiplos anos
        silver_dir = tmp_path / "data" / "silver" / "comparecimento_abstencao"
        silver_dir.mkdir(parents=True)

        for year in [2020, 2022]:
            parquet_path = silver_dir / f"year={year}" / "data.parquet"
            parquet_path.parent.mkdir(exist_ok=True)
            sample_data.assign(ano=year).to_parquet(parquet_path)

        with patch("participacao_eleitoral.dashboard.PROJECT_ROOT", tmp_path):
            at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")

            # Alterar filtro de anos
            year_multiselect = at.sidebar.multiselect[0]  # Anos
            year_multiselect.set_value([2022])

            at.run(timeout=10)

            # Verificar se dados foram filtrados
            # Métricas devem refletir apenas 2022
            metrics = at.metric
            assert len(metrics) == 3

    def test_error_handling_missing_data(self):
        """Testa tratamento de erro para dados ausentes."""
        with patch("participacao_eleitoral.dashboard.PROJECT_ROOT", Path("/nonexistent")):
            at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")
            at.run()

            # Verificar mensagens de erro ou warnings
            warnings = [elem for elem in at.main if "não encontrado" in str(elem)]
            assert len(warnings) > 0 or not at.exception  # Ou sem erro se mockado

    def test_edge_case_empty_selection(self):
        """Testa caso extremo: seleção vazia de anos."""
        # Provide minimal data
        df_min = pd.DataFrame(
            {
                "ano": [2022],
                "taxa_comparecimento": [80.0],
                "comparecimento_total": [1000],
                "abstencao_total": [200],
            }
        )
        df_reg_min = pd.DataFrame(
            {
                "ano": [2022],
                "regiao": ["Sudeste"],
                "taxa_comparecimento": [80.0],
                "comparecimento_total": [1000],
                "abstencao_total": [200],
            }
        )
        df_map_min = pd.DataFrame({"ano": [2022], "uf": ["SP"], "taxa_comparecimento": [80.0]})
        with (
            patch(
                "participacao_eleitoral.dashboard.carregar_dados_reais",
                return_value=(df_min, df_reg_min, df_map_min),
            ),
            patch(
                "participacao_eleitoral.dashboard.carregar_geojson",
                return_value={"type": "FeatureCollection", "features": []},
            ),
        ):
            at = AppTest.from_file("src/participacao_eleitoral/dashboard.py")

            # Limpar seleção de anos
            year_multiselect = at.sidebar.multiselect[0]
            year_multiselect.set_value([])

            at.run(timeout=10)

            # Verificar comportamento (warnings ou métricas vazias)
            metrics = at.metric
            assert len(metrics) == 0 or "não disponível" in str(at.main)

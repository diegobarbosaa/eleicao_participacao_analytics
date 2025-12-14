"""Testes para geração de URLs do TSE."""

import pytest
from participacao_eleitoral.ingestion.tse_urls import TSEDatasetURLs


class TestTSEDatasetURLs:
    """Testa construção de URLs do TSE."""
    
    def test_url_comparecimento_2024(self):
        """Testa URL para comparecimento 2024."""
        url = TSEDatasetURLs.get_comparecimento_url(2024)
        
        assert "https://cdn.tse.jus.br" in url
        assert "perfil_comparecimento_abstencao" in url
        assert "2024.zip" in url
    
    def test_url_comparecimento_2022(self):
        """Testa URL para comparecimento 2022."""
        url = TSEDatasetURLs.get_comparecimento_url(2022)
        
        assert "2022.zip" in url
    
    def test_listar_anos_disponiveis(self):
        """Testa listagem de anos disponíveis."""
        anos = TSEDatasetURLs.listar_anos_disponiveis()
        
        assert isinstance(anos, list)
        assert 2024 in anos
        assert 2022 in anos
        assert len(anos) > 0
    
    def test_anos_ordenados_decrescente(self):
        """Testa que anos estão em ordem decrescente."""
        anos = TSEDatasetURLs.listar_anos_disponiveis()
        
        assert anos == sorted(anos, reverse=True)
        assert anos[0] > anos[-1]  # Primeiro > Último
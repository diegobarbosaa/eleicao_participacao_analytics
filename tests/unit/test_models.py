"""Testes para models.py"""

from datetime import datetime
from pathlib import Path

import pytest
from participacao_eleitoral.ingestion.models import DatasetTSE, IngestaoMetadata


class TestDatasetTSE:
    """Testes para DatasetTSE."""
    
    def test_criar_dataset_valido(self):
        """Testa criação de DatasetTSE válido."""
        dataset = DatasetTSE(
            ano=2024,
            nome_arquivo="teste.csv",
            url_download="https://exemplo.com/teste.zip",
        )
        
        assert dataset.ano == 2024
        assert dataset.nome_arquivo == "teste.csv"
        assert "https://" in dataset.url_download
    
    def test_ano_invalido_menor(self):
        """Testa que ano < 2000 é rejeitado."""
        with pytest.raises(ValueError, match="Ano inválido"):
            DatasetTSE(
                ano=1999,
                nome_arquivo="teste.csv",
                url_download="https://exemplo.com/teste.zip",
            )
    
    def test_ano_invalido_maior(self):
        """Testa que ano > 2030 é rejeitado."""
        with pytest.raises(ValueError, match="Ano inválido"):
            DatasetTSE(
                ano=2031,
                nome_arquivo="teste.csv",
                url_download="https://exemplo.com/teste.zip",
            )
    
    def test_url_sem_http(self):
        """Testa que URL sem http/https é rejeitada."""
        with pytest.raises(ValueError, match="URL inválida"):
            DatasetTSE(
                ano=2024,
                nome_arquivo="teste.csv",
                url_download="ftp://exemplo.com/teste.zip",
            )


class TestIngestaoMetadata:
    """Testes para IngestaoMetadata."""
    
    def test_criar_metadata_sucesso(self):
        """Testa criação de metadata com sucesso."""
        dataset = DatasetTSE(
            ano=2024,
            nome_arquivo="teste.csv",
            url_download="https://exemplo.com/teste.zip",
        )
        
        inicio = datetime.now()
        fim = datetime.now()
        
        metadata = IngestaoMetadata(
            dataset=dataset,
            timestamp_inicio=inicio,
            timestamp_fim=fim,
            arquivo_destino=Path("/tmp/teste.parquet"),
            tamanho_bytes=1024000,
            linhas_ingeridas=10000,
            checksum_sha256="abc123",
            sucesso=True,
        )
        
        assert metadata.sucesso is True
        assert metadata.linhas_ingeridas == 10000
        assert metadata.tamanho_bytes == 1024000
    
    def test_duracao_segundos(self):
        """Testa cálculo de duração."""
        dataset = DatasetTSE(
            ano=2024,
            nome_arquivo="teste.csv",
            url_download="https://exemplo.com/teste.zip",
        )
        
        inicio = datetime(2024, 1, 1, 10, 0, 0)
        fim = datetime(2024, 1, 1, 10, 1, 30)  # 90 segundos depois
        
        metadata = IngestaoMetadata(
            dataset=dataset,
            timestamp_inicio=inicio,
            timestamp_fim=fim,
            arquivo_destino=Path("/tmp/teste.parquet"),
            tamanho_bytes=1024000,
            linhas_ingeridas=10000,
            checksum_sha256="abc123",
            sucesso=True,
        )
        
        assert metadata.duracao_segundos == 90.0
    
    def test_to_dict(self):
        """Testa conversão para dict."""
        dataset = DatasetTSE(
            ano=2024,
            nome_arquivo="teste.csv",
            url_download="https://exemplo.com/teste.zip",
        )
        
        metadata = IngestaoMetadata(
            dataset=dataset,
            timestamp_inicio=datetime.now(),
            timestamp_fim=datetime.now(),
            arquivo_destino=Path("/tmp/teste.parquet"),
            tamanho_bytes=1024000,
            linhas_ingeridas=10000,
            checksum_sha256="abc123",
            sucesso=True,
        )
        
        dict_data = metadata.to_dict()
        
        assert dict_data["ano"] == 2024
        assert dict_data["sucesso"] is True
        assert dict_data["linhas_ingeridas"] == 10000
        assert "duracao_segundos" in dict_data
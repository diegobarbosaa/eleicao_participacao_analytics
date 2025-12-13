"""Testes unitários para o downloader do TSE."""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import zipfile

import httpx
import pytest

from participacao_eleitoral.ingestion.downloader import TSEDownloader
from participacao_eleitoral.ingestion.models import DatasetTSE


@pytest.fixture
def mock_dataset():
    """Fixture que cria um dataset de exemplo para testes."""
    return DatasetTSE(
        ano=2024,
        nome_arquivo="teste.csv",
        url_download="https://exemplo.com/teste.csv",
    )


@pytest.fixture
def mock_dataset_zip():
    """Dataset com URL .zip."""
    return DatasetTSE(
        ano=2024,
        nome_arquivo="teste.csv",
        url_download="https://exemplo.com/teste.zip",
    )


def test_downloader_initialization():
    """Testa que o downloader é criado com configurações corretas."""
    downloader = TSEDownloader()
    
    # Verifica que o cliente HTTP foi configurado
    assert isinstance(downloader.client, httpx.Client)
    assert downloader.client.timeout.read == 300  # timeout configurado


@patch("httpx.Client.stream")
def test_download_csv_sucesso(mock_stream, mock_dataset, tmp_path):
    """Testa download bem-sucedido de CSV direto (sem ZIP)."""
    # Configurar o mock para simular resposta HTTP
    mock_response = Mock()
    mock_response.headers = {"content-length": "1024"}
    mock_response.raise_for_status = Mock()  # Não lança exceção
    mock_response.iter_bytes = Mock(return_value=[b"coluna1;coluna2\n", b"valor1;valor2\n"])
    
    # Context manager mock
    mock_stream.return_value.__enter__ = Mock(return_value=mock_response)
    mock_stream.return_value.__exit__ = Mock(return_value=False)
    
    # Executar o download
    downloader = TSEDownloader()
    output_path = tmp_path / "teste.csv"
    
    arquivo, tamanho, checksum = downloader.download_csv(mock_dataset, output_path)
    
    # Assertions (verificações)
    assert arquivo.exists(), "Arquivo deveria ter sido criado"
    assert tamanho > 0, "Tamanho deveria ser maior que zero"
    assert len(checksum) == 64, "SHA-256 tem 64 caracteres hexadecimais"
    assert arquivo.read_text() == "coluna1;coluna2\nvalor1;valor2\n"


@patch("httpx.Client.stream")
def test_download_zip_com_extracao(mock_stream, mock_dataset_zip, tmp_path):
    """Testa download de ZIP com extração automática."""
    # Criar um ZIP real temporário para testar extração
    zip_path = tmp_path / "temp_test.zip"
    csv_content = b"coluna1;coluna2\nvalor1;valor2\n"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("dados.csv", csv_content)
    
    # Mock da resposta HTTP retornando o conteúdo do ZIP
    mock_response = Mock()
    mock_response.headers = {"content-length": str(zip_path.stat().st_size)}
    mock_response.raise_for_status = Mock()
    
    # Ler ZIP real e retornar em chunks
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()
    
    mock_response.iter_bytes = Mock(return_value=[zip_bytes])
    
    mock_stream.return_value.__enter__ = Mock(return_value=mock_response)
    mock_stream.return_value.__exit__ = Mock(return_value=False)
    
    # Executar download
    downloader = TSEDownloader()
    output_path = tmp_path / "output" / "teste.csv"
    
    arquivo, tamanho, checksum = downloader.download_csv(mock_dataset_zip, output_path)
    
    # Verificações
    assert arquivo.exists(), "CSV extraído deveria existir"
    assert arquivo.suffix == ".csv", "Deveria ser um CSV"
    assert arquivo.read_bytes() == csv_content, "Conteúdo deveria ser igual"
    assert not (tmp_path / "output" / "teste.zip").exists(), "ZIP deveria ter sido deletado"


@patch("httpx.Client.stream")
def test_download_retry_on_failure(mock_stream, mock_dataset, tmp_path):
    """Testa que o downloader retenta após falha temporária."""
    # Primeira chamada falha, segunda sucede
    mock_response_fail = Mock()
    mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Server Error", 
        request=Mock(), 
        response=Mock(status_code=500)
    )
    
    mock_response_success = Mock()
    mock_response_success.headers = {"content-length": "100"}
    mock_response_success.raise_for_status = Mock()
    mock_response_success.iter_bytes = Mock(return_value=[b"dados\n"])
    
    # Configurar mock para falhar 1x e suceder depois
    mock_stream.return_value.__enter__.side_effect = [
        mock_response_fail,
        mock_response_success,
    ]
    mock_stream.return_value.__exit__ = Mock(return_value=False)
    
    downloader = TSEDownloader()
    output_path = tmp_path / "teste.csv"
    
    # Deve suceder na segunda tentativa
    arquivo, tamanho, checksum = downloader.download_csv(mock_dataset, output_path)
    
    assert arquivo.exists()
    # Verifica que houve 2 chamadas (1 falha + 1 sucesso)
    assert mock_stream.call_count == 2


@patch("httpx.Client.stream")
def test_download_falha_apos_max_retries(mock_stream, mock_dataset, tmp_path):
    """Testa que exceção é levantada após 3 falhas consecutivas."""
    # Simula falha em todas as tentativas
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Server Error", 
        request=Mock(), 
        response=Mock(status_code=500)
    )
    mock_stream.return_value.__enter__ = Mock(return_value=mock_response)
    mock_stream.return_value.__exit__ = Mock(return_value=False)
    
    downloader = TSEDownloader()
    output_path = tmp_path / "teste.csv"
    
    # Deve levantar exceção após 3 tentativas
    with pytest.raises(httpx.HTTPStatusError):
        downloader.download_csv(mock_dataset, output_path)
    
    # Verifica que tentou 3 vezes
    assert mock_stream.call_count == 3


def test_extract_zip_multiplos_csvs(tmp_path):
    """Testa extração de ZIP com múltiplos CSVs (pega o maior)."""
    # Criar ZIP com múltiplos CSVs
    zip_path = tmp_path / "multi.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("pequeno.csv", b"a;b\n1;2\n")
        zf.writestr("grande.csv", b"a;b\n" + b"1;2\n" * 100)  # Maior
        zf.writestr("medio.csv", b"a;b\n" + b"1;2\n" * 10)
    
    downloader = TSEDownloader()
    target_path = tmp_path / "output.csv"
    
    # Extrair
    result_path = downloader._extract_zip(zip_path, target_path)
    
    # Deve ter extraído o maior
    assert result_path.exists()
    assert result_path == target_path
    
    # ✅ CORRIGIDO: grande.csv tem 404 bytes (4 + 100*4)
    assert len(result_path.read_text()) == 404, "Deveria ter extraído o arquivo grande"
    
    # Verificar que é realmente o arquivo grande
    num_linhas = len(result_path.read_text().strip().split('\n'))
    assert num_linhas == 101, "Deveria ter 101 linhas (header + 100 dados)"


def test_extract_zip_sem_csv_raise_error(tmp_path):
    """Testa que erro é levantado se ZIP não contém CSV."""
    # Criar ZIP sem CSV
    zip_path = tmp_path / "sem_csv.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("dados.txt", b"texto")
        zf.writestr("dados.json", b"{}")
    
    downloader = TSEDownloader()
    target_path = tmp_path / "output.csv"
    
    # Deve levantar ValueError
    with pytest.raises(ValueError, match="Nenhum CSV encontrado"):
        downloader._extract_zip(zip_path, target_path)


@patch("httpx.Client.stream")
def test_checksum_sha256_correto(mock_stream, mock_dataset, tmp_path):
    """Verifica que checksum SHA-256 é calculado corretamente."""
    import hashlib
    
    conteudo = b"teste de checksum\n"
    checksum_esperado = hashlib.sha256(conteudo).hexdigest()
    
    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(conteudo))}
    mock_response.raise_for_status = Mock()
    mock_response.iter_bytes = Mock(return_value=[conteudo])
    
    mock_stream.return_value.__enter__ = Mock(return_value=mock_response)
    mock_stream.return_value.__exit__ = Mock(return_value=False)
    
    downloader = TSEDownloader()
    output_path = tmp_path / "teste.csv"
    
    _, _, checksum = downloader.download_csv(mock_dataset, output_path)
    
    assert checksum == checksum_esperado, "Checksum deveria ser idêntico"
"""Testes adicionais para o Downloader para aumentar cobertura"""

import zipfile

import pytest

from participacao_eleitoral.core.entities import Dataset
from participacao_eleitoral.ingestion.downloader import TSEDownloader


def test_downloader_detecta_zip(tmp_path, settings, logger, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """
    Downloader deve detectar automaticamente se é ZIP.
    """
    downloader = TSEDownloader(settings=settings, logger=logger)

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://example.com/dataset.zip",
    )

    output_path = tmp_path / "output.csv"

    # Criar ZIP fake
    zip_path = tmp_path / "test.zip"
    csv_content = b"ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n2022;12345;Recife;PE;1000;800;200\n"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("data.csv", csv_content)

    # Mock do httpx para retornar o ZIP
    httpx_mock.add_response(
        url=dataset.url_origem,
        content=zip_path.read_bytes(),
        headers={"content-length": str(len(zip_path.read_bytes()))},
    )

    # Download
    result = downloader.download_csv(dataset, output_path)

    # Verificar
    assert output_path.exists()
    assert result.csv_path == output_path
    assert result.tamanho_bytes > 0
    assert len(result.checksum_sha256) > 0


def test_downloader_nao_e_zip(tmp_path, settings, logger, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """
    Downloader deve funcionar com CSV direto (sem ZIP).
    """
    downloader = TSEDownloader(settings=settings, logger=logger)

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://example.com/dataset.csv",
    )

    output_path = tmp_path / "output.csv"

    # Mock do httpx para retornar CSV direto
    csv_content = b"ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n2022;12345;Recife;PE;1000;800;200\n"
    httpx_mock.add_response(
        url=dataset.url_origem,
        content=csv_content,
        headers={"content-length": str(len(csv_content))},
    )

    # Download
    result = downloader.download_csv(dataset, output_path)

    # Verificar
    assert output_path.exists()
    assert result.csv_path == output_path
    assert result.tamanho_bytes == len(csv_content)


def test_downloader_escolhe_maior_csv_em_zip(tmp_path, settings, logger, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """
    Se ZIP contém múltiplos CSVs, deve escolher o maior.
    """
    downloader = TSEDownloader(settings=settings, logger=logger)

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://example.com/dataset.zip",
    )

    output_path = tmp_path / "output.csv"

    # Criar ZIP com múltiplos CSVs
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("small.csv", b"data\n1\n")  # 6 bytes
        zf.writestr("large.csv", b"data\n1\n2\n3\n4\n5\n")  # 18 bytes
        zf.writestr("medium.csv", b"data\n1\n2\n")  # 10 bytes

    # Mock do httpx
    httpx_mock.add_response(
        url=dataset.url_origem,
        content=zip_path.read_bytes(),
        headers={"content-length": str(len(zip_path.read_bytes()))},
    )

    # Download
    result = downloader.download_csv(dataset, output_path)

    # Verificar que foi escolhido o maior CSV
    content = output_path.read_bytes()
    assert b"large.csv" not in content  # Nome não está no conteúdo
    assert result.tamanho_bytes > 10  # Deve ser o maior


def test_downloader_remove_zip_apos_extracao(tmp_path, settings, logger, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """
    Downloader deve remover arquivo ZIP temporário após extração.
    """
    downloader = TSEDownloader(settings=settings, logger=logger)

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://example.com/dataset.zip",
    )

    output_path = tmp_path / "output.csv"
    zip_temp_path = tmp_path / "raw.zip"

    # Criar ZIP fake
    zip_path = tmp_path / "test.zip"
    csv_content = b"ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n2022;12345;Recife;PE;1000;800;200\n"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("data.csv", csv_content)

    # Mock do httpx
    httpx_mock.add_response(
        url=dataset.url_origem,
        content=zip_path.read_bytes(),
        headers={"content-length": str(len(zip_path.read_bytes()))},
    )

    # Download
    downloader.download_csv(dataset, output_path)

    # Verificar que ZIP foi removido
    assert not zip_temp_path.exists(), "ZIP temporário deve ser removido"


def test_downloader_calcula_checksum_corretamente(tmp_path, settings, logger, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """
    Downloader deve calcular checksum SHA-256 corretamente.
    """
    downloader = TSEDownloader(settings=settings, logger=logger)

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://example.com/dataset.csv",
    )

    output_path = tmp_path / "output.csv"

    # Conteúdo conhecido
    csv_content = b"test content\n"

    # Mock do httpx
    httpx_mock.add_response(
        url=dataset.url_origem,
        content=csv_content,
        headers={"content-length": str(len(csv_content))},
    )

    # Download
    result = downloader.download_csv(dataset, output_path)

    # Verificar checksum (calcular manualmente)
    import hashlib

    expected_hash = hashlib.sha256(csv_content).hexdigest()

    assert result.checksum_sha256 == expected_hash


def test_downloader_falha_sem_csv_no_zip(tmp_path, settings, logger, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """
    Downloader deve falhar se ZIP não contém nenhum CSV.
    """
    downloader = TSEDownloader(settings=settings, logger=logger)

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://example.com/dataset.zip",
    )

    output_path = tmp_path / "output.csv"

    # Criar ZIP sem CSV
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("data.txt", b"not a csv")

    # Mock do httpx
    httpx_mock.add_response(
        url=dataset.url_origem,
        content=zip_path.read_bytes(),
        headers={"content-length": str(len(zip_path.read_bytes()))},
    )

    # Download deve falhar
    with pytest.raises(ValueError, match="Nenhum CSV encontrado"):
        downloader.download_csv(dataset, output_path)

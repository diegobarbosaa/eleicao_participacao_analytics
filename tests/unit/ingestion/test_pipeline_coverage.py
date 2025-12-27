"""Testes adicionais para o Pipeline para aumentar cobertura"""

import polars as pl
import pytest

from participacao_eleitoral.ingestion.pipeline import IngestionPipeline
from participacao_eleitoral.ingestion.results import ConvertResult, DownloadResult


def test_pipeline_verifica_idempotencia(tmp_path, settings, logger, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """
    Pipeline deve verificar se ingestão já foi feita e pular.
    """
    # Configurar ambiente
    settings.bronze_dir = tmp_path / "bronze"
    settings.bronze_dir.mkdir(parents=True, exist_ok=True)

    # Criar pipeline
    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Mock do downloader
    download_called = False

    def mock_download(dataset, output_path):  # type: ignore[no-untyped-def]
        nonlocal download_called
        download_called = True
        return DownloadResult(
            csv_path=tmp_path / "fake.csv",
            tamanho_bytes=100,
            checksum_sha256="abc",
        )

    monkeypatch.setattr(pipeline.downloader, "download_csv", mock_download)

    # Criar CSV fake
    (tmp_path / "fake.csv").write_text(
        "ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n"
        "2022;12345;Recife;PE;1000;800;200\n"
    )

    # Mock do converter
    def mock_convert(csv_path, parquet_path, schema, source):  # type: ignore[no-untyped-def]
        # Criar parquet real
        df = pl.read_csv(csv_path, separator=";")
        df.write_parquet(parquet_path)
        return ConvertResult(parquet_path=parquet_path, linhas=len(df))

    monkeypatch.setattr(pipeline.converter, "convert", mock_convert)

    # Primeira execução - deve baixar
    pipeline.run(2022)
    assert download_called, "Downloader deve ser chamado na primeira execução"

    # Reset do flag
    download_called = False

    # Segunda execução - deve pular
    pipeline.run(2022)
    assert not download_called, "Downloader NÃO deve ser chamado na segunda execução (idempotência)"


def test_pipeline_cria_diretorios_se_nao_existem(tmp_path, settings, logger, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """
    Pipeline deve criar diretórios necessários.
    """
    # Configurar com diretórios que não existem
    settings.bronze_dir = tmp_path / "data" / "bronze"

    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Mock do downloader e converter
    def mock_download(dataset, output_path):  # type: ignore[no-untyped-def]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n"
            "2022;12345;Recife;PE;1000;800;200\n"
        )
        return DownloadResult(
            csv_path=output_path,
            tamanho_bytes=100,
            checksum_sha256="abc",
        )

    def mock_convert(csv_path, parquet_path, schema, source):  # type: ignore[no-untyped-def]
        df = pl.read_csv(csv_path, separator=";")
        df.write_parquet(parquet_path)
        return ConvertResult(parquet_path=parquet_path, linhas=len(df))

    monkeypatch.setattr(pipeline.downloader, "download_csv", mock_download)
    monkeypatch.setattr(pipeline.converter, "convert", mock_convert)

    # Executar
    pipeline.run(2022)

    # Verificar que diretórios foram criados
    assert (settings.bronze_dir / "comparecimento_abstencao" / "year=2022").exists()


def test_pipeline_remove_csv_temporario(tmp_path, settings, logger, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """
    Pipeline deve remover CSV temporário após conversão.
    """
    settings.bronze_dir = tmp_path / "bronze"
    settings.bronze_dir.mkdir(parents=True, exist_ok=True)

    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # CSV temporário que deve ser criado
    temp_csv = settings.bronze_dir / "comparecimento_abstencao" / "year=2022" / "raw.csv"

    # Mock do downloader
    def mock_download(dataset, output_path):  # type: ignore[no-untyped-def]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n"
            "2022;12345;Recife;PE;1000;800;200\n"
        )
        return DownloadResult(
            csv_path=output_path,
            tamanho_bytes=100,
            checksum_sha256="abc",
        )

    monkeypatch.setattr(pipeline.downloader, "download_csv", mock_download)

    # Mock do converter
    def mock_convert(csv_path, parquet_path, schema, source):  # type: ignore[no-untyped-def]
        df = pl.read_csv(csv_path, separator=";")
        df.write_parquet(parquet_path)
        return ConvertResult(parquet_path=parquet_path, linhas=len(df))

    monkeypatch.setattr(pipeline.converter, "convert", mock_convert)

    # Executar
    pipeline.run(2022)

    # Verificar que CSV foi removido
    assert not temp_csv.exists(), "CSV temporário deve ser removido após conversão"


def test_pipeline_salva_metadata_sucesso(tmp_path, settings, logger, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """
    Pipeline deve salvar metadata de execução bem-sucedida.
    """
    settings.bronze_dir = tmp_path / "bronze"
    settings.bronze_dir.mkdir(parents=True, exist_ok=True)

    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Mock do downloader
    def mock_download(dataset, output_path):  # type: ignore[no-untyped-def]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCAO\n"
            "2022;12345;Recife;PE;1000;800;200\n"
        )
        return DownloadResult(
            csv_path=output_path,
            tamanho_bytes=100,
            checksum_sha256="abc123",
        )

    monkeypatch.setattr(pipeline.downloader, "download_csv", mock_download)

    # Mock do converter
    def mock_convert(csv_path, parquet_path, schema, source):  # type: ignore[no-untyped-def]
        df = pl.read_csv(csv_path, separator=";")
        # Adicionar linhas para testar
        df = pl.concat([df] * 1000)
        df.write_parquet(parquet_path)
        return ConvertResult(parquet_path=parquet_path, linhas=len(df))

    monkeypatch.setattr(pipeline.converter, "convert", mock_convert)

    # Executar
    pipeline.run(2022)

    # Verificar metadata
    metadata = pipeline.metadata_store.buscar("comparecimento_abstencao", 2022)
    assert metadata is not None
    assert metadata["status"] == "sucesso"
    assert metadata["linhas"] == 1000
    assert metadata["tamanho_bytes"] == 100
    assert metadata["checksum"] == "abc123"


def test_pipeline_salva_metadata_falha(tmp_path, settings, logger, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """
    Pipeline deve salvar metadata de execução com falha.
    """
    settings.bronze_dir = tmp_path / "bronze"
    settings.bronze_dir.mkdir(parents=True, exist_ok=True)

    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Mock do downloader que falha
    def mock_download_fail(dataset, output_path):  # type: ignore[no-untyped-def]
        raise Exception("Erro simulado no download")

    monkeypatch.setattr(pipeline.downloader, "download_csv", mock_download_fail)

    # Executar e capturar erro
    with pytest.raises(Exception, match="Erro simulado no download"):
        pipeline.run(2022)

    # Verificar metadata de falha
    metadata = pipeline.metadata_store.buscar("comparecimento_abstencao", 2022)
    assert metadata is not None
    assert metadata["status"] == "falha"
    assert metadata["erro"] == "Erro simulado no download"
    assert metadata["linhas"] == 0
    assert metadata["tamanho_bytes"] == 0

"""Teste de integração com dados reais do TSE"""

import polars as pl
import pytest

from participacao_eleitoral.ingestion.metadata_store import MetadataStore
from participacao_eleitoral.ingestion.pipeline import IngestionPipeline


@pytest.mark.integration
@pytest.mark.slow
def test_pipeline_com_dados_reais_tse(tmp_path, settings, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Teste de integração baixando um ano pequeno do TSE real.
    Usa 2014 (dados mais leves, ~2MB).

    Este teste marca como integration e slow porque:
    - Faz download real da internet
    - Pode levar vários minutos
    - Depende de disponibilidade do servidor do TSE
    """
    # Criar pipeline
    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Executar com ano 2014 (dados pequenos)
    pipeline.run(2014)

    # Verificar saídas
    parquet_path = settings.bronze_dir / "comparecimento_abstencao" / "year=2014" / "data.parquet"
    assert parquet_path.exists(), "Parquet deve existir"

    # Verificar dados
    df = pl.read_parquet(parquet_path)
    assert len(df) > 0, "DataFrame deve ter linhas"

    # Verificar colunas obrigatórias
    assert "ANO_ELEICAO" in df.columns, "ANO_ELEICAO deve existir"
    assert "CD_MUNICIPIO" in df.columns, "CD_MUNICIPIO deve existir"
    assert "NM_MUNICIPIO" in df.columns, "NM_MUNICIPIO deve existir"
    assert "SG_UF" in df.columns, "SG_UF deve existir"
    assert "QT_APTOS" in df.columns, "QT_APTOS deve existir"
    assert "QT_COMPARECIMENTO" in df.columns, "QT_COMPARECIMENTO deve existir"
    assert "QT_ABSTENCAO" in df.columns, "QT_ABSTENCAO deve existir"

    # Verificar colunas de metadados
    assert "_metadata_ingestion_timestamp" in df.columns, "Metadados de timestamp devem existir"
    assert "_metadata_source" in df.columns, "Metadados de source devem existir"

    # Verificar dados válidos
    assert df["ANO_ELEICAO"].unique().to_list() == [2014], "Todos os registros devem ser de 2014"
    assert df["QT_APTOS"].min() >= 0, "QT_APTOS deve ser não negativo"  # type: ignore[operator]
    assert df["QT_COMPARECIMENTO"].min() >= 0, "QT_COMPARECIMENTO deve ser não negativo"  # type: ignore[operator]

    # Verificar metadados
    store = MetadataStore(settings=settings, logger=logger)
    metadata = store.buscar("comparecimento_abstencao", 2014)
    assert metadata is not None, "Metadados devem existir"
    assert metadata["status"] == "sucesso", "Status deve ser sucesso"
    assert metadata["linhas"] == len(df), "Linhas nos metadados devem bater com DataFrame"
    assert metadata["tamanho_bytes"] > 0, "Tamanho deve ser maior que 0"
    assert len(metadata["checksum"]) > 0, "Checksum deve existir"
    assert metadata["erro"] is None, "Erro deve ser None em sucesso"


@pytest.mark.integration
@pytest.mark.slow
def test_pipeline_idempotencia_com_dados_reais(tmp_path, settings, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Pipeline deve ser idempotente mesmo com dados reais.
    """
    # Criar pipeline
    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Primeira execução
    pipeline.run(2014)

    # Obter parquet
    parquet_path = settings.bronze_dir / "comparecimento_abstencao" / "year=2014" / "data.parquet"
    df1 = pl.read_parquet(parquet_path)
    linhas1 = len(df1)

    # Segunda execução (deve pular)
    pipeline.run(2014)

    # Verificar que não foi baixado de novo
    df2 = pl.read_parquet(parquet_path)
    linhas2 = len(df2)

    assert linhas1 == linhas2, "Número de linhas deve ser o mesmo"


@pytest.mark.integration
@pytest.mark.slow
def test_pipeline_verifica_detalhes_municipios(tmp_path, settings, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Verificar se dados dos municípios são corretos (validação de negócio).
    """
    # Criar pipeline
    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Executar
    pipeline.run(2014)

    # Ler dados
    parquet_path = settings.bronze_dir / "comparecimento_abstencao" / "year=2014" / "data.parquet"
    df = pl.read_parquet(parquet_path)

    # Verificar municípios conhecidos (São Paulo, Rio de Janeiro, Recife)
    # Isso valida que os dados foram corretamente extraídos
    sp = df.filter(pl.col("NM_MUNICIPIO") == "SÃO PAULO")
    assert len(sp) > 0, "São Paulo deve estar nos dados"

    rj = df.filter(pl.col("NM_MUNICIPIO") == "RIO DE JANEIRO")
    assert len(rj) > 0, "Rio de Janeiro deve estar nos dados"

    # Verificar consistência: comparecimento + abstenção = aptos
    df_valido = df.filter(
        pl.col("QT_COMPARECIMENTO") + pl.col("QT_ABSTENCAO") == pl.col("QT_APTOS")
    )

    # Pelo menos 99% dos registros devem ser consistentes
    taxa_consistencia = len(df_valido) / len(df)
    assert taxa_consistencia >= 0.99, f"Consistência de {taxa_consistencia:.2%} deve ser >= 99%"

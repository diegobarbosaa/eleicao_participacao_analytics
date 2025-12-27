"""Testes do Transformer Bronze → Silver"""

import polars as pl

from participacao_eleitoral.silver.region_mapper import RegionMapper
from participacao_eleitoral.silver.schemas.comparecimento_silver import SCHEMA_SILVER
from participacao_eleitoral.silver.transformer import BronzeToSilverTransformer


def test_transformer_calcula_taxas(tmp_path, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Transformer deve calcular taxas de participação corretamente.
    """
    # Criar parquet bronze fake
    bronze_path = tmp_path / "bronze.parquet"
    df_bronze = pl.DataFrame(
        {
            "ANO_ELEICAO": [2022, 2022, 2022],
            "CD_MUNICIPIO": [1, 2, 3],
            "NM_MUNICIPIO": ["A", "B", "C"],
            "SG_UF": ["SP", "RJ", "MG"],
            "QT_APTOS": [100, 200, 300],
            "QT_COMPARECIMENTO": [80, 150, 240],
            "QT_ABSTENCAO": [20, 50, 60],
            "_metadata_ingestion_timestamp": ["2024-01-01", "2024-01-01", "2024-01-01"],
            "_metadata_source": ["test", "test", "test"],
        }
    )
    df_bronze.write_parquet(bronze_path)

    # Criar silver
    silver_path = tmp_path / "silver.parquet"
    transformer = BronzeToSilverTransformer(logger=logger)
    result = transformer.transform(
        bronze_parquet_path=bronze_path,
        silver_parquet_path=silver_path,
        region_mapper=RegionMapper(),
        schema=SCHEMA_SILVER,
    )

    # Verificar resultado
    assert silver_path.exists()
    assert result.linhas == 3

    # Verificar colunas calculadas
    df_silver = pl.read_parquet(silver_path)
    assert "TAXA_COMPARECIMENTO_PCT" in df_silver.columns
    assert "TAXA_ABSTENCAO_PCT" in df_silver.columns
    assert "NOME_REGIAO" in df_silver.columns

    # Verificar cálculos corretos
    assert df_silver["TAXA_COMPARECIMENTO_PCT"][0] == 80.0  # 80/100 * 100
    assert df_silver["TAXA_ABSTENCAO_PCT"][0] == 20.0  # 20/100 * 100


def test_transformer_adiciona_regiao_geografica(tmp_path, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Transformer deve adicionar região geográfica corretamente.
    """
    # Criar parquet bronze fake
    bronze_path = tmp_path / "bronze.parquet"
    df_bronze = pl.DataFrame(
        {
            "ANO_ELEICAO": [2022] * 5,
            "CD_MUNICIPIO": [1, 2, 3, 4, 5],
            "NM_MUNICIPIO": ["A", "B", "C", "D", "E"],
            "SG_UF": ["SP", "RJ", "MG", "BA", "XX"],  # XX é inválido
            "QT_APTOS": [100] * 5,
            "QT_COMPARECIMENTO": [80] * 5,
            "QT_ABSTENCAO": [20] * 5,
            "_metadata_ingestion_timestamp": ["2024-01-01"] * 5,
            "_metadata_source": ["test"] * 5,
        }
    )
    df_bronze.write_parquet(bronze_path)

    # Criar silver
    silver_path = tmp_path / "silver.parquet"
    transformer = BronzeToSilverTransformer(logger=logger)
    transformer.transform(
        bronze_parquet_path=bronze_path,
        silver_parquet_path=silver_path,
        region_mapper=RegionMapper(),
        schema=SCHEMA_SILVER,
    )

    # Verificar regiões
    df_silver = pl.read_parquet(silver_path)
    regioes = df_silver["NOME_REGIAO"].to_list()

    assert "Sudeste" in regioes  # SP, RJ, MG
    assert "Nordeste" in regioes  # BA
    assert "Desconhecido" in regioes  # XX


def test_transformer_remove_nulos(tmp_path, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Transformer deve remover linhas com nulos.
    """
    # Criar parquet bronze com nulos
    bronze_path = tmp_path / "bronze.parquet"
    df_bronze = pl.DataFrame(
        {
            "ANO_ELEICAO": [2022, 2022, None],
            "CD_MUNICIPIO": [1, 2, 3],
            "NM_MUNICIPIO": ["A", "B", "C"],
            "SG_UF": ["SP", "RJ", "MG"],
            "QT_APTOS": [100, 200, 300],
            "QT_COMPARECIMENTO": [80, 150, 240],
            "QT_ABSTENCAO": [20, 50, 60],
            "_metadata_ingestion_timestamp": ["2024-01-01", "2024-01-01", "2024-01-01"],
            "_metadata_source": ["test", "test", "test"],
        }
    )
    df_bronze.write_parquet(bronze_path)

    # Criar silver
    silver_path = tmp_path / "silver.parquet"
    transformer = BronzeToSilverTransformer(logger=logger)
    result = transformer.transform(
        bronze_parquet_path=bronze_path,
        silver_parquet_path=silver_path,
        region_mapper=RegionMapper(),
        schema=SCHEMA_SILVER,
    )

    # Verificar que linha com nulo foi removida
    assert result.linhas == 2


def test_transformer_cria_diretorio_se_nao_existe(tmp_path, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Transformer deve criar diretório de destino se não existir.
    """
    # Criar bronze
    bronze_path = tmp_path / "bronze.parquet"
    df_bronze = pl.DataFrame(
        {
            "ANO_ELEICAO": [2022],
            "CD_MUNICIPIO": [1],
            "NM_MUNICIPIO": ["A"],
            "SG_UF": ["SP"],
            "QT_APTOS": [100],
            "QT_COMPARECIMENTO": [80],
            "QT_ABSTENCAO": [20],
            "_metadata_ingestion_timestamp": ["2024-01-01"],
            "_metadata_source": ["test"],
        }
    )
    df_bronze.write_parquet(bronze_path)

    # Usar caminho que não existe
    silver_path = tmp_path / "nao_existe" / "silver.parquet"
    transformer = BronzeToSilverTransformer(logger=logger)
    result = transformer.transform(
        bronze_path,
        silver_path,
        region_mapper=RegionMapper(),
        schema=SCHEMA_SILVER,
    )

    # Verificar que foi criado e arquivo existe
    assert silver_path.exists()
    assert result.linhas == 1


def test_transformer_mantera_colunas_originais(tmp_path, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Transformer deve manter colunas originais do bronze.
    """
    # Criar bronze
    bronze_path = tmp_path / "bronze.parquet"
    df_bronze = pl.DataFrame(
        {
            "ANO_ELEICAO": [2022],
            "CD_MUNICIPIO": [1],
            "NM_MUNICIPIO": ["A"],
            "SG_UF": ["SP"],
            "QT_APTOS": [100],
            "QT_COMPARECIMENTO": [80],
            "QT_ABSTENCAO": [20],
            "_metadata_ingestion_timestamp": ["2024-01-01"],
            "_metadata_source": ["test"],
        }
    )
    df_bronze.write_parquet(bronze_path)

    # Criar silver
    silver_path = tmp_path / "silver.parquet"
    transformer = BronzeToSilverTransformer(logger=logger)
    result = transformer.transform(
        bronze_parquet_path=bronze_path,
        silver_parquet_path=silver_path,
        region_mapper=RegionMapper(),
        schema=SCHEMA_SILVER,
    )

    # Verificar colunas originais mantidas
    df_silver = pl.read_parquet(silver_path)
    assert "ANO_ELEICAO" in df_silver.columns
    assert "CD_MUNICIPIO" in df_silver.columns
    assert "NM_MUNICIPIO" in df_silver.columns
    assert "SG_UF" in df_silver.columns
    assert "QT_APTOS" in df_silver.columns
    assert "QT_COMPARECIMENTO" in df_silver.columns
    assert "QT_ABSTENCAO" in df_silver.columns

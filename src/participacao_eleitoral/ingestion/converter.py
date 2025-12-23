from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from participacao_eleitoral.utils.logger import ModernLogger

from .results import ConvertResult


class CSVToParquetConverter:
    """
    Converte CSVs do TSE para Parquet otimizado.

    Responsabilidades:
    - parsing de CSV
    - aplicação de schema
    - enriquecimento técnico
    - escrita columnar

    NÃO conhece:
    - Airflow
    - DuckDB
    - regras de negócio
    """

    def __init__(self, logger: ModernLogger):
        # Logger é injetado (não criado aqui)
        # - reaproveitamento em CLI, Airflow, testes
        self.logger = logger

    def convert(
        self,
        csv_path: Path,
        parquet_path: Path,
        schema: dict[str, type[pl.DataType]] | None,
        source: str,
    ) -> ConvertResult:
        """
        Converte um CSV em Parquet.

        Parâmetros:
        - csv_path: caminho do CSV já validado
        - parquet_path: destino final
        - schema: schema explícito (contrato de dados)
        - source: identificador lógico da origem
        """

        self.logger.info(
            "conversao_iniciada",
            origem=csv_path.name,
            destino=parquet_path.name,
        )

        # Garante que o diretório de saída existe
        parquet_path.parent.mkdir(parents=True, exist_ok=True)

        lf = pl.scan_csv(
            csv_path,
            separator=";",  # padrão TSE
            encoding="utf8-lossy",  # tolera encoding ruim
            null_values=["#NULO#", "#NE#"],  # padrões do TSE
            schema_overrides=schema,  # contrato explícito
        )

        lf = lf.with_columns(
            [
                # Timestamp UTC da ingestão
                pl.lit(datetime.now(UTC)).alias("_metadata_ingestion_timestamp"),
                # Identificador lógico da fonte
                pl.lit(source).alias("_metadata_source"),
            ]
        )

        lf.sink_parquet(
            parquet_path,
            compression="zstd",  # ótimo custo-benefício
            compression_level=3,  # balanceado
            statistics=True,  # melhora query pushdown
            row_group_size=100_000,  # bom para leitura analítica
        )

        # Conta linhas lendo apenas metadados do Parquet
        linhas = pl.scan_parquet(parquet_path).select(pl.len()).collect().item()

        self.logger.success(
            "conversao_concluida",
            linhas=linhas,
        )

        return ConvertResult(
            parquet_path=parquet_path,
            linhas=linhas,
        )

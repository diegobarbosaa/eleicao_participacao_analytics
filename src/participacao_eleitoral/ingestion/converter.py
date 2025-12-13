from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from participacao_eleitoral.utils.logger import ModernLogger


class CSVToParquetConverter:
    """Converte CSVs do TSE para Parquet otimizado"""

    def __init__(self, logger: ModernLogger):
        self.logger = logger

    def convert(
        self,
        csv_path: Path,
        parquet_path: Path,
        schema: dict[str, pl.DataType] | None = None,
        source: str | None = None,
    ) -> tuple[Path, int]:


        self.logger.info(
            "conversao_iniciada",
            origem=csv_path.name,
            destino=parquet_path.name,
        )

        parquet_path.parent.mkdir(parents=True, exist_ok=True)

        scan_kwargs = {
            "separator": ";",
            "encoding": "utf8-lossy",
            "null_values": ["#NULO#", "#NE#"],
        }

        if schema:
            scan_kwargs["schema_overrides"] = schema

        lf = pl.scan_csv(csv_path, **scan_kwargs)
        df = lf.collect()
        linhas = df.height

        df = df.with_columns([
            pl.lit(datetime.now(timezone.utc)).alias("_metadata_ingestion_timestamp"),
            pl.lit(source or "unknown").alias("_metadata_source"),
        ])


        df.write_parquet(
            parquet_path,
            compression="zstd",
            compression_level=3,
            statistics=True,
            row_group_size=100_000,
        )

        tamanho_csv = csv_path.stat().st_size / 1024 / 1024
        tamanho_parquet = parquet_path.stat().st_size / 1024 / 1024
        reducao = (1 - tamanho_parquet / tamanho_csv) * 100

        self.logger.success(
            "conversao_concluida",
            linhas=linhas,
            tamanho_csv_mb=round(tamanho_csv, 2),
            tamanho_parquet_mb=round(tamanho_parquet, 2),
            reducao_percent=round(reducao, 2),
        )

        return parquet_path, linhas
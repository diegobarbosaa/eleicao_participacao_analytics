"""Transformador da camada Bronze para Silver"""

from pathlib import Path

import polars as pl

from participacao_eleitoral.silver.region_mapper import RegionMapper
from participacao_eleitoral.utils.logger import ModernLogger

from .results import SilverTransformResult


class BronzeToSilverTransformer:
    """
    Transforma dados do bronze para silver.

    Esta classe:
    - adiciona colunas calculadas (taxas)
    - padroniza formatos
    - remove nulos
    - adiciona informações geográficas

    Ela NÃO:
    - faz download de dados
    - valida os schemas de bronze
    - conhece Airflow
    """

    def __init__(self, logger: ModernLogger):
        self.logger = logger

    def transform(
        self,
        bronze_parquet_path: Path,
        silver_parquet_path: Path,
        region_mapper: RegionMapper,
        schema: dict[str, type[pl.DataType]] | None,
    ) -> SilverTransformResult:
        """
        Transforma dados do bronze para silver.

        Fluxo:
        1. Ler Parquet bronze (eager - todos os dados usados)
        2. Calcular taxas de participação
        3. Adicionar região geográfica
        4. Remover nulos
        5. Escrever Parquet silver

        Args:
            bronze_parquet_path: Caminho do arquivo Parquet bronze
            silver_parquet_path: Caminho de destino para Parquet silver
            region_mapper: Mapeador de UF para região
            schema: Schema explícito (contrato de dados)

        Returns:
            SilverTransformResult com caminho e número de linhas
        """
        self.logger.info(
            "transformacao_iniciada",
            bronze=str(bronze_parquet_path.name),
            silver=str(silver_parquet_path.name),
        )

        # 1. Ler bronze (eager - todos os dados serão usados)
        df = pl.read_parquet(bronze_parquet_path)

        linhas_antes = len(df)
        self.logger.info("bronze_lido", linhas=linhas_antes)

        # 2. Calcular taxas de participação
        df = df.with_columns(
            [
                # Taxa de comparecimento: (comparecimento / aptos) * 100
                ((pl.col("QT_COMPARECIMENTO") / pl.col("QT_APTOS")) * 100).alias(
                    "TAXA_COMPARECIMENTO_PCT"
                ),
                # Taxa de abstenção: (abstenções / aptos) * 100
                ((pl.col("QT_ABSTENCAO") / pl.col("QT_APTOS")) * 100).alias("TAXA_ABSTENCAO_PCT"),
            ]
        )

        # 3. Adicionar região geográfica (usando apply Python)
        df = df.with_columns(
            [
                pl.col("SG_UF")
                .map_elements(region_mapper.get_regiao, return_dtype=pl.Utf8)
                .alias("NOME_REGIAO")
            ]
        )

        # 4. Remover linhas com nulos (garantir qualidade)
        df = df.drop_nulls()

        linhas_depois = len(df)
        linhas_removidas = linhas_antes - linhas_depois

        if linhas_removidas > 0:
            self.logger.warning(
                "nulos_removidos",
                linhas_removidas=linhas_removidas,
                pct_removido=f"{(linhas_removidas / linhas_antes) * 100:.2f}%",
            )

        # 5. Garantir diretório de destino existe
        silver_parquet_path.parent.mkdir(parents=True, exist_ok=True)

        # 6. Escrever silver
        df.write_parquet(
            silver_parquet_path,
            compression="zstd",
            compression_level=3,
            statistics=True,
            row_group_size=100_000,
        )

        self.logger.success(
            "transformacao_concluida",
            linhas=linhas_depois,
            arquivo=silver_parquet_path.name,
        )

        return SilverTransformResult(
            silver_path=silver_parquet_path,
            linhas=linhas_depois,
        )

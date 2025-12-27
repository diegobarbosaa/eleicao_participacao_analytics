"""Orquestrador da transformação Bronze → Silver"""

from datetime import UTC, datetime

from participacao_eleitoral.config import Settings
from participacao_eleitoral.core.entities import Dataset
from participacao_eleitoral.core.enums import StatusIngestao
from participacao_eleitoral.silver.region_mapper import RegionMapper
from participacao_eleitoral.silver.schemas.comparecimento_silver import (
    SCHEMA_SILVER,
    validar_schema_silver_contra_contrato,
)
from participacao_eleitoral.utils.logger import ModernLogger

from .metadata_store import SilverMetadataStore
from .results import SilverTransformResult
from .transformer import BronzeToSilverTransformer


class SilverTransformationPipeline:
    """
    Orquestrador do fluxo de transformação Bronze → Silver.

    Esta classe:
    - coordena as etapas
    - aplica idempotência (DuckDB + arquivo)
    - conecta core e infra

    Ela NÃO conhece:
    - Airflow
    - CLI
    - detalhes internos de Polars ou HTTP
    """

    def __init__(
        self,
        settings: Settings,
        logger: ModernLogger,
        metadata_store: SilverMetadataStore | None = None,
    ):
        self.settings = settings
        self.logger = logger

        # MetadataStore pode ser injetado (útil para testes)
        self.metadata_store = metadata_store or SilverMetadataStore(
            settings=settings,
            logger=logger,
        )

        # Transformer
        self.transformer = BronzeToSilverTransformer(logger=logger)

        # Region Mapper
        self.region_mapper = RegionMapper()

    def run(self, ano: int) -> None:
        """
        Executa o pipeline completo para um ano específico.

        Fluxo:
        1. Cria entidade do domínio
        2. Verifica idempotência (DuckDB + arquivo)
        3. Valida schema vs contrato
        4. Verifica se bronze existe
        5. Transforma
        6. Persiste metadados
        """

        inicio = datetime.now(UTC)

        dataset = Dataset(
            nome="comparecimento_abstencao",
            ano=ano,
            url_origem=f"{self.settings.bronze_dir}/comparecimento_abstencao/year={ano}/data.parquet",
        )

        # Verifica se já existe transformação bem-sucedida
        registro = self.metadata_store.buscar(dataset.nome, ano)

        # Idempotência nível 1: Verifica metadata
        if registro and registro["status"] == StatusIngestao.SUCESSO.value:
            # Idempotência nível 2: Verifica se arquivo ainda existe
            silver_path = self.settings.silver_dir / dataset.nome / f"year={ano}" / "data.parquet"
            if silver_path.exists():
                self.logger.info(
                    "transformacao_ja_realizada",
                    dataset=dataset.nome,
                    ano=ano,
                )
                return

        # Garante que o schema físico respeita o domínio
        validar_schema_silver_contra_contrato()

        try:
            self.logger.info(
                "pipeline_silver_iniciado",
                dataset=dataset.nome,
                ano=ano,
            )

            # Verifica se bronze existe
            bronze_path = (
                self.settings.bronze_dir
                / "comparecimento_abstencao"
                / f"year={ano}"
                / "data.parquet"
            )

            if not bronze_path.exists():
                self.logger.warning(
                    "bronze_nao_existe_skip",
                    ano=ano,
                    bronze_path=str(bronze_path),
                )
                return

            silver_path = self.settings.silver_dir / dataset.nome / f"year={ano}" / "data.parquet"

            result: SilverTransformResult = self.transformer.transform(
                bronze_parquet_path=bronze_path,
                silver_parquet_path=silver_path,
                region_mapper=self.region_mapper,
                schema=SCHEMA_SILVER,
            )

            fim = datetime.now(UTC)

            metadata = {
                "dataset": dataset.nome,
                "ano": dataset.ano,
                "status": StatusIngestao.SUCESSO.value,
                "inicio": inicio.astimezone(UTC).isoformat(),
                "fim": fim.astimezone(UTC).isoformat(),
                "duracao_segundos": (fim - inicio).total_seconds(),
                "linhas_antes": result.linhas,
                "linhas_depois": result.linhas,
                "erro": None,
            }

            self.metadata_store.salvar(metadata)

            self.logger.success(
                "pipeline_silver_concluido",
                dataset=dataset.nome,
                ano=ano,
                linhas=result.linhas,
            )

        except Exception as exc:
            fim = datetime.now(UTC)

            self.logger.error(
                "pipeline_silver_falhou",
                dataset=dataset.nome,
                ano=ano,
                erro=str(exc),
                tipo_erro=type(exc).__name__,
            )

            metadata = {
                "dataset": dataset.nome,
                "ano": dataset.ano,
                "status": StatusIngestao.FALHA.value,
                "inicio": inicio.astimezone(UTC).isoformat(),
                "fim": fim.astimezone(UTC).isoformat(),
                "duracao_segundos": (fim - inicio).total_seconds(),
                "linhas_antes": 0,
                "linhas_depois": 0,
                "erro": str(exc),
            }

            self.metadata_store.salvar(metadata)

            raise

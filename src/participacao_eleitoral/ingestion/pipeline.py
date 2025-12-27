from datetime import UTC, datetime

# Configurações globais do projeto (paths, timeouts, etc.)
from participacao_eleitoral.config import Settings

# ===== CORE (domínio) =====
# Entidade lógica do dataset
from participacao_eleitoral.core.entities import Dataset

# Status da ingestão (regra de negócio)
from participacao_eleitoral.core.enums import StatusIngestao

# Funções de construção de metadados (regra de negócio)
from participacao_eleitoral.core.services import (
    construir_metadata_falha,
    construir_metadata_sucesso,
)

# Conversor CSV → Parquet
from participacao_eleitoral.ingestion.converter import CSVToParquetConverter

# ===== INGESTION (infra) =====
# Downloader HTTP / ZIP
from participacao_eleitoral.ingestion.downloader import TSEDownloader

# Persistência de metadados
from participacao_eleitoral.ingestion.metadata_store import MetadataStore

# Objetos de retorno entre etapas
from participacao_eleitoral.ingestion.results import ConvertResult, DownloadResult

# Schema físico + validação contra contrato lógico
from participacao_eleitoral.ingestion.schemas.comparecimento import (
    SCHEMA_COMPARECIMENTO,
    validar_schema_contra_contrato,
)

# Logger estruturado (não print)
from participacao_eleitoral.utils.logger import ModernLogger


class IngestionPipeline:
    """
    Orquestrador do fluxo de ingestão.

    Esta classe:
    - coordena as etapas
    - aplica idempotência
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
        metadata_store: MetadataStore | None = None,
    ):
        # Configurações globais
        self.settings = settings

        # Logger é injetado (permite CLI, Airflow, testes)
        self.logger = logger

        # Inicializa componentes de infra
        self.downloader = TSEDownloader(settings=settings, logger=logger)
        self.converter = CSVToParquetConverter(logger=logger)

        # MetadataStore pode ser injetado (útil para testes)
        self.metadata_store = metadata_store or MetadataStore(
            settings=settings,
            logger=logger,
        )

    def run(self, ano: int) -> None:
        """
        Executa o pipeline completo para um ano específico.

        Fluxo:
        1. Cria entidade do domínio
        2. Verifica idempotência
        3. Valida schema vs contrato
        4. Download
        5. Conversão
        6. Persistência de metadados
        """

        inicio = datetime.now(UTC)

        dataset = Dataset(
            nome="comparecimento_abstencao",
            ano=ano,
            url_origem=f"https://cdn.tse.jus.br/estatistica/sead/odsele/"
            f"perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_{ano}.zip",
        )

        # Verifica se já existe ingestão bem-sucedida
        registro = self.metadata_store.buscar(dataset.nome, ano)

        if registro and registro["status"] == StatusIngestao.SUCESSO.value:
            self.logger.info(
                "ingestao_ja_realizada",
                dataset=dataset.nome,
                ano=ano,
            )
            return

        # Garante que o schema físico respeita o domínio
        validar_schema_contra_contrato()

        try:
            self.logger.info(
                "pipeline_iniciado",
                dataset=dataset.nome,
                ano=ano,
            )

            dataset_dir = self.settings.bronze_dir / dataset.nome / f"year={ano}"
            dataset_dir.mkdir(parents=True, exist_ok=True)

            raw_csv_path = dataset_dir / "raw.csv"
            parquet_path = dataset_dir / "data.parquet"

            download: DownloadResult = self.downloader.download_csv(
                dataset=dataset,
                output_path=raw_csv_path,
            )

            source = f"tse:{dataset.nome}:{ano}"

            convert: ConvertResult = self.converter.convert(
                csv_path=download.csv_path,
                parquet_path=parquet_path,
                schema=SCHEMA_COMPARECIMENTO,
                source=source,
            )

            if raw_csv_path.exists():
                raw_csv_path.unlink()
                self.logger.info("raw_csv_removido", arquivo=raw_csv_path.name)

            fim = datetime.now(UTC)

            metadata = construir_metadata_sucesso(
                dataset=dataset,
                inicio=inicio,
                fim=fim,
                linhas=convert.linhas,
                tamanho_bytes=download.tamanho_bytes,
                checksum=download.checksum_sha256,
            )

            self.metadata_store.salvar(metadata)

            self.logger.success(
                "pipeline_concluido",
                dataset=dataset.nome,
                ano=ano,
                linhas=convert.linhas,
            )

        except Exception as exc:
            fim = datetime.now(UTC)

            self.logger.error(
                "pipeline_falhou",
                dataset=dataset.nome,
                ano=ano,
                erro=str(exc),
                tipo_erro=type(exc).__name__,
            )

            metadata = construir_metadata_falha(
                dataset=dataset,
                inicio=inicio,
                fim=fim,
                erro=str(exc),
            )

            self.metadata_store.salvar(metadata)

            raise

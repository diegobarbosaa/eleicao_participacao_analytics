from datetime import datetime, timezone
from pathlib import Path

from participacao_eleitoral.config import Settings
from participacao_eleitoral.ingestion.schemas import SCHEMA_COMPARECIMENTO
from participacao_eleitoral.ingestion.converter import CSVToParquetConverter
from participacao_eleitoral.ingestion.downloader import TSEDownloader
from participacao_eleitoral.ingestion.metadata_store import MetadataStore
from participacao_eleitoral.ingestion.models import (
    DatasetTSE,
    IngestaoMetadata,
    StatusIngestao,
)
from participacao_eleitoral.ingestion.tse_urls import TSEDatasetURLs
from participacao_eleitoral.utils.logger import ModernLogger


class IngestionPipeline:
    """Orquestra o fluxo completo de ingestão de dados do TSE"""

    DATASET_NAME = "comparecimento_abstencao"

    def __init__(
        self,
        settings: Settings,
        logger: ModernLogger,
        metadata_store: MetadataStore | None = None,
    ):
        self.settings = settings
        self.logger = logger

        self.bronze_dir = self.settings.bronze_dir
        self.bronze_dir.mkdir(parents=True, exist_ok=True)

        self.downloader = TSEDownloader(settings=self.settings, logger=self.logger)
        self.converter = CSVToParquetConverter(logger=self.logger)
        self.metadata_store = metadata_store or MetadataStore(
            settings=self.settings,
            logger=self.logger,
        )

        self.logger.info("pipeline_inicializado")

    def run(self, ano: int) -> IngestaoMetadata:
        timestamp_inicio = datetime.now(timezone.utc)

        dataset = DatasetTSE(
            ano=ano,
            nome_arquivo="raw.csv",
            url_download=TSEDatasetURLs.get_comparecimento_url(ano),
        )

        # 📁 bronze/comparecimento_abstencao/year=2024/
        dataset_dir = (
            self.bronze_dir
            / self.DATASET_NAME
            / f"year={ano}"
        )
        dataset_dir.mkdir(parents=True, exist_ok=True)

        raw_csv_path = dataset_dir / "raw.csv"
        parquet_path = dataset_dir / "data.parquet"

        # 0️⃣ Idempotência: não rebaixar se já existe sucesso
        registro = self.metadata_store.buscar_por_ano(ano)
        if (
            registro
            and registro["status"] == StatusIngestao.SUCESSO
            and parquet_path.exists()
        ):
            self.logger.info(
                "ingestao_ja_existente",
                dataset=self.DATASET_NAME,
                ano=ano,
                arquivo=parquet_path.name,
            )
            return IngestaoMetadata.from_dict(registro)

        try:
            self.logger.info(
                "pipeline_iniciado",
                dataset=self.DATASET_NAME,
                ano=ano,
            )

            # 1️⃣ Download
            csv_path, tamanho, checksum = self.downloader.download_csv(
                dataset=dataset,
                output_path=raw_csv_path,
            )

            # 2️⃣ Converter
            source = f"tse:{self.DATASET_NAME}:{ano}"

            parquet_final, linhas = self.converter.convert(
                csv_path=csv_path,
                parquet_path=parquet_path,
                schema=SCHEMA_COMPARECIMENTO,
                source=source,
            )

            # 3️⃣ (Opcional) remover raw.csv
            if raw_csv_path.exists():
                raw_csv_path.unlink()
                self.logger.info("raw_csv_removido", arquivo=raw_csv_path.name)

            status = StatusIngestao.SUCESSO
            mensagem_erro = None

            self.logger.success(
                "pipeline_concluido",
                dataset=self.DATASET_NAME,
                ano=ano,
                linhas=linhas,
                tamanho_mb=round(tamanho / 1024 / 1024, 2),
            )

        except Exception as exc:
            status = StatusIngestao.FALHA
            mensagem_erro = str(exc)

            self.logger.error(
                "pipeline_falhou",
                dataset=self.DATASET_NAME,
                ano=ano,
                erro=mensagem_erro,
                tipo_erro=type(exc).__name__,
            )
            raise

        finally:
            timestamp_fim = datetime.now(timezone.utc)

            metadata = IngestaoMetadata(
                dataset=dataset,
                timestamp_inicio=timestamp_inicio,
                timestamp_fim=timestamp_fim,
                arquivo_destino=parquet_path,
                tamanho_bytes=tamanho if status == StatusIngestao.SUCESSO else 0,
                linhas_ingeridas=linhas if status == StatusIngestao.SUCESSO else 0,
                checksum_sha256=checksum if status == StatusIngestao.SUCESSO else "",
                status=status,
                mensagem_erro=mensagem_erro,
            )

            self.metadata_store.salvar(metadata)

        return metadata
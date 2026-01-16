import hashlib
import zipfile
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from participacao_eleitoral.config import Settings
from participacao_eleitoral.core.entities import Dataset
from participacao_eleitoral.utils.logger import ModernLogger

from .results import DownloadResult


class TSEDownloader:
    """
    Download, extração de ZIPs e cálculo de checksum para garantir integridade.

    NÃO: parsing de dados, validação de schema ou persistência analítica.
    """

    def __init__(self, settings: Settings, logger: ModernLogger):
        self.settings = settings
        self.logger = logger

        self.client = httpx.Client(
            timeout=httpx.Timeout(self.settings.request_timeout),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _download_http(self, url: str, destino: Path) -> tuple[int, str]:
        """
        Baixa um arquivo via HTTP de forma resiliente.

        Retry é aplicado APENAS aqui, porque:
        - falhas HTTP são transitórias
        - falhas de parsing NÃO devem ser reexecutadas
        """

        self.logger.info("download_iniciado", url=url)

        # Garante que o diretório de saída existe
        destino.parent.mkdir(parents=True, exist_ok=True)

        # Inicializa hash SHA-256
        hasher = hashlib.sha256()
        tamanho = 0

        # Streaming HTTP (não carrega tudo em memória)
        with self.client.stream("GET", url) as response:
            response.raise_for_status()

            with open(destino, "wb") as f:
                # Leitura em chunks
                for chunk in response.iter_bytes(self.settings.chunk_size):
                    f.write(chunk)
                    hasher.update(chunk)
                    tamanho += len(chunk)

        return tamanho, hasher.hexdigest()

    def download_csv(self, dataset: Dataset, output_path: Path) -> DownloadResult:
        """
        Orquestra o download do dataset.

        Decide automaticamente:
        - se é ZIP
        - se precisa extrair
        - qual arquivo final será retornado
        """

        # Verifica se a URL aponta para um ZIP
        is_zip = dataset.url_origem.endswith(".zip")

        # Caminho temporário de download
        download_path = output_path.parent / "raw.zip" if is_zip else output_path

        # Etapa 1: download resiliente
        tamanho, checksum = self._download_http(
            dataset.url_origem,
            download_path,
        )

        self.logger.success(
            "download_concluido",
            arquivo=download_path.name,
            tamanho_mb=round(tamanho / 1024 / 1024, 2),
        )

        # Etapa 2: se ZIP, extrair CSV
        if is_zip:
            return self._handle_zip(download_path, output_path)

        # Se não é ZIP, o próprio CSV já é o resultado final
        return DownloadResult(
            csv_path=download_path,
            tamanho_bytes=tamanho,
            checksum_sha256=checksum,
        )

    def _handle_zip(self, zip_path: Path, target_csv_path: Path) -> DownloadResult:
        """
        Extrai o CSV correto de um arquivo ZIP.

        Estratégia:
        - se houver múltiplos CSVs, escolhe o MAIOR
        """

        self.logger.info("extraindo_zip", arquivo=zip_path.name)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Lista apenas arquivos CSV
            csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]

            if not csv_files:
                raise ValueError(f"Nenhum CSV encontrado em {zip_path}")

            # Se houver mais de um CSV, escolhe o maior
            if len(csv_files) > 1:
                self.logger.warning(
                    "multiplos_csvs_encontrados",
                    quantidade=len(csv_files),
                )
                csv_files.sort(
                    key=lambda f: zip_ref.getinfo(f).file_size,
                    reverse=True,
                )

            csv_filename = csv_files[0]
            zip_ref.extract(csv_filename, target_csv_path.parent)

        extracted_path = target_csv_path.parent / csv_filename

        # Remove arquivo antigo se existir (idempotência)
        if target_csv_path.exists():
            target_csv_path.unlink()

        # Renomeia para o nome final esperado
        extracted_path.rename(target_csv_path)

        # Remove ZIP temporário
        zip_path.unlink(missing_ok=True)

        hasher = hashlib.sha256()
        tamanho = 0

        with open(target_csv_path, "rb") as f:
            for chunk in iter(lambda: f.read(self.settings.chunk_size), b""):
                hasher.update(chunk)
                tamanho += len(chunk)

        self.logger.success(
            "zip_extraido",
            csv_final=target_csv_path.name,
            tamanho_csv_mb=round(tamanho / 1024 / 1024, 2),
        )

        return DownloadResult(
            csv_path=target_csv_path,
            tamanho_bytes=tamanho,
            checksum_sha256=hasher.hexdigest(),
        )

    def close(self) -> None:
        """Fecha explicitamente o cliente HTTP."""
        self.client.close()

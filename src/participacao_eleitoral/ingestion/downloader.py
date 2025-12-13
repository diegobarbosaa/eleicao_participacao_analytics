import hashlib
import zipfile
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from participacao_eleitoral.config import Settings
from participacao_eleitoral.ingestion.models import DatasetTSE
from participacao_eleitoral.utils.logger import ModernLogger


class TSEDownloader:
    """Cliente para download de dados do TSE com retry e validação"""

    def __init__(self, settings: Settings, logger: ModernLogger):
        self.settings = settings
        self.logger = logger

        self.client = httpx.Client(
            timeout=httpx.Timeout(self.settings.request_timeout),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5),
        )

    # 🔁 Retry APENAS no HTTP
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _download_http(self, url: str, dest: Path) -> tuple[int, str]:
        self.logger.info("download_iniciado", url=url)

        dest.parent.mkdir(parents=True, exist_ok=True)

        hasher = hashlib.sha256()
        size = 0

        with self.client.stream("GET", url) as response:
            response.raise_for_status()

            with open(dest, "wb") as f:
                for chunk in response.iter_bytes(self.settings.chunk_size):
                    f.write(chunk)
                    hasher.update(chunk)
                    size += len(chunk)

        return size, hasher.hexdigest()

    def download_csv(self, dataset: DatasetTSE, output_path: Path):
        is_zip = dataset.url_download.endswith(".zip")

        download_path = (
            output_path.parent / "raw.zip"
            if is_zip
            else output_path
        )

        # ⬇️ Download resiliente
        size, checksum = self._download_http(
            dataset.url_download,
            download_path,
        )

        self.logger.success(
            "download_concluido",
            arquivo=download_path.name,
            tamanho_mb=round(size / 1024 / 1024, 2),
        )

        # 📦 Pós-processamento SEM retry
        if is_zip:
            csv_path, csv_size, csv_checksum = self._handle_zip(
                download_path,
                output_path,
            )
            return csv_path, csv_size, csv_checksum

        return download_path, size, checksum

    def _handle_zip(
        self,
        zip_path: Path,
        target_csv_path: Path,
    ) -> tuple[Path, int, str]:

        self.logger.info("extraindo_zip", arquivo=zip_path.name)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]

            if not csv_files:
                raise ValueError(f"Nenhum CSV encontrado em {zip_path}")

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

        # 🔒 Garantir idempotência no Windows e Linux
        if target_csv_path.exists():
            self.logger.warning(
                "raw_csv_existente_removido",
                arquivo=target_csv_path.name,
            )
            target_csv_path.unlink()

        extracted_path.rename(target_csv_path)
        zip_path.unlink(missing_ok=True)

        # 🔐 Checksum streaming do CSV final
        hasher = hashlib.sha256()
        size = 0

        with open(target_csv_path, "rb") as f:
            for chunk in iter(lambda: f.read(self.settings.chunk_size), b""):
                hasher.update(chunk)
                size += len(chunk)

        self.logger.success(
            "zip_extraido",
            csv_final=target_csv_path.name,
            tamanho_csv_mb=round(size / 1024 / 1024, 2),
        )

        return target_csv_path, size, hasher.hexdigest()

    def close(self) -> None:
        self.client.close()
"""Configuração centralizada do projeto usando Pydantic Settings"""

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_project_root() -> Path:
    """
    Raiz do projeto.

    - Dentro do container Astro, este arquivo fica em:
      /usr/local/airflow/src/participacao_eleitoral/config.py

      Então: parents[2] -> /usr/local/airflow
    - Fora do container, quando você roda o projeto diretamente,
      continua valendo a mesma lógica.
    """
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # ===== AMBIENTE =====
    environment: Literal["development", "staging", "production"] = "development"

    # ===== DIRETÓRIOS =====
    # Raiz do projeto (dentro do container: /usr/local/airflow)
    project_root: Path = Field(default_factory=_default_project_root)

    # Diretórios derivados da raiz (propriedades computadas)
    @property
    def data_dir(self) -> Path:
        """Diretório de dados derivado de project_root."""
        return self.project_root / "data"

    @property
    def logs_dir(self) -> Path:
        """Diretório de logs derivado de project_root."""
        return self.project_root / "logs"

    @property
    def bronze_dir(self) -> Path:
        """Diretório bronze derivado de project_root."""
        return self.project_root / "data" / "bronze"

    @property
    def silver_dir(self) -> Path:
        """Diretório silver derivado de project_root."""
        return self.project_root / "data" / "silver"

    @property
    def gold_dir(self) -> Path:
        """Diretório gold derivado de project_root."""
        return self.project_root / "data" / "gold"

    # ===== TSE API =====
    tse_base_url: str = "https://cdn.tse.jus.br/estatistica/sead/odsele"
    request_timeout: int = Field(default=300, ge=10, le=3600)
    max_retries: int = Field(default=3, ge=1, le=10)

    # ===== LOGGING =====
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "console"
    show_timestamps: bool = False

    # ===== PERFORMANCE =====
    chunk_size: int = Field(default=8192, ge=1024)
    polars_threads: int = Field(
        default_factory=lambda: os.cpu_count() or 4,
        ge=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PARTICIPACAO_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        return v.upper()

    @field_validator("tse_base_url", mode="before")
    @classmethod
    def validate_tse_base_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {v}")
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"URL must be HTTP or HTTPS: {v}")
        return v

    @field_validator("project_root", mode="after")
    @classmethod
    def validate_project_root(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Project root does not exist: {v}")
        return v

    def setup_dirs(self) -> None:
        """
        Garante que os diretórios principais existem.

        Computed fields já criam os diretórios automaticamente
        ao acessá-los, mas mantemos este método para
        compatibilidade e garantia explícita.
        """
        for path in (
            self.data_dir,
            self.bronze_dir,
            self.silver_dir,
            self.gold_dir,
            self.logs_dir,
        ):
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError:
                # Silenciar erro de criação de diretório (comum em containers read-only)
                pass

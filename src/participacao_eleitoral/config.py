"""Configuração centralizada do projeto usando Pydantic Settings"""

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_project_root() -> Path:
    """
    Raiz do projeto.

    - Dentro do container Astro, este arquivo fica em:
      /usr/local/airflow/src/participacao_eleitoral/config.py

      Então: parents[2] -> /usr/local/airflow
    - Fora do container, quando você roda o projeto direto,
      continua valendo a mesma lógica.
    """
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # ===== AMBIENTE =====
    environment: Literal["development", "staging", "production"] = "development"

    # ===== DIRETÓRIOS =====
    # Raiz do projeto (dentro do container: /usr/local/airflow)
    project_root: Path = Field(default_factory=_default_project_root)

    # Diretórios derivados da raiz
    data_dir: Path = Field(default=None)  # type: ignore
    logs_dir: Path = Field(default=None)  # type: ignore
    bronze_dir: Path = Field(default=None)  # type: ignore
    silver_dir: Path = Field(default=None)  # type: ignore
    gold_dir: Path = Field(default=None)  # type: ignore

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

    # ===== FEATURE FLAGS (DESLABILITADAS POR PADRÃO) =====
    enable_strict_validation: bool = Field(default=False, description="Validação estrita de schema")
    enable_performance_logging: bool = Field(
        default=False, description="Logs detalhados de performance"
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

    @field_validator(
        "data_dir",
        "logs_dir",
        "bronze_dir",
        "silver_dir",
        "gold_dir",
        mode="before",
    )
    @classmethod
    def _resolve_dirs(cls, v, info) -> Path:
        """
        Monta os caminhos de dados e logs a partir de project_root.

        Dentro do container, se project_root = /usr/local/airflow:
        - data_dir   -> /usr/local/airflow/data
        - logs_dir   -> /usr/local/airflow/logs
        - bronze_dir -> /usr/local/airflow/data/bronze
        etc.
        """
        project_root = info.data["project_root"]

        mapping = {
            "data_dir": project_root / "data",
            "logs_dir": project_root / "logs",
            "bronze_dir": project_root / "data" / "bronze",
            "silver_dir": project_root / "data" / "silver",
            "gold_dir": project_root / "data" / "gold",
        }

        return mapping[info.field_name]

    def setup_dirs(self) -> None:
        """
        Garante que os diretórios principais existem.
        Se não existirem, cria (sem erro se já existirem).
        Em caso de falha, imprime aviso no console.
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
            except OSError as e:
                print(f"Aviso: Falha ao criar diretório {path}: {e}")

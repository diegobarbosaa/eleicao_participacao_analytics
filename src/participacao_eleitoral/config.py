"""Configuração centralizada do projeto usando Pydantic Settings"""

from pathlib import Path
from typing import Literal
import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_project_root() -> Path:
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # ===== AMBIENTE =====
    environment: Literal["development", "staging", "production"] = "development"

    # ===== DIRETÓRIOS =====
    project_root: Path = Field(default_factory=_default_project_root)

    data_dir: Path = Field(default=None)
    logs_dir: Path = Field(default=None)

    bronze_dir: Path = Field(default=None)
    silver_dir: Path = Field(default=None)
    gold_dir: Path = Field(default=None)

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

    @field_validator(
        "data_dir",
        "logs_dir",
        "bronze_dir",
        "silver_dir",
        "gold_dir",
        mode="before",
    )
    @classmethod
    def _resolve_dirs(cls, v, info):
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
        for path in (
            self.data_dir,
            self.bronze_dir,
            self.silver_dir,
            self.gold_dir,
            self.logs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
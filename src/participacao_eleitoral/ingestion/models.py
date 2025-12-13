"""Modelos de dados para ingestão"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TypedDict


class StatusIngestao(Enum):
    SUCESSO = "sucesso"
    FALHA = "falha"
    PARCIAL = "parcial"


@dataclass(frozen=True)
class DatasetTSE:
    """Metadados de um dataset do TSE"""

    ano: int
    nome_arquivo: str
    url_download: str

    def __post_init__(self):
        if not (2000 <= self.ano <= 2030):
            raise ValueError(f"Ano inválido: {self.ano}")

        if not self.url_download.startswith(("http://", "https://")):
            raise ValueError(f"URL inválida: {self.url_download}")


class IngestaoMetadataDict(TypedDict):
    ano: int
    nome_arquivo: str
    url_download: str
    timestamp_inicio: str
    timestamp_fim: str
    arquivo_destino: str
    tamanho_bytes: int
    linhas_ingeridas: int
    checksum_sha256: str
    status: str
    mensagem_erro: str | None
    duracao_segundos: float
    tamanho_mb: float


@dataclass
class IngestaoMetadata:
    """Metadados de uma ingestão realizada"""

    dataset: DatasetTSE
    timestamp_inicio: datetime
    timestamp_fim: datetime
    arquivo_destino: Path
    tamanho_bytes: int
    linhas_ingeridas: int
    checksum_sha256: str
    status: StatusIngestao
    mensagem_erro: str | None = None

    def __post_init__(self):
        # Timezone obrigatório
        for campo in ("timestamp_inicio", "timestamp_fim"):
            ts = getattr(self, campo)
            if ts.tzinfo is None:
                raise ValueError(f"{campo} deve conter timezone (UTC)")

        # Path absoluto
        if not self.arquivo_destino.is_absolute():
            raise ValueError("arquivo_destino deve ser um caminho absoluto")

        # Invariantes de negócio
        if self.status == StatusIngestao.SUCESSO and self.mensagem_erro:
            raise ValueError("Ingestão com sucesso não pode ter mensagem de erro")

        if self.status == StatusIngestao.FALHA and not self.mensagem_erro:
            raise ValueError("Ingestão com falha deve conter mensagem de erro")

        if self.timestamp_fim < self.timestamp_inicio:
            raise ValueError("timestamp_fim não pode ser anterior ao timestamp_inicio")

    @property
    def duracao_segundos(self) -> float:
        return (self.timestamp_fim - self.timestamp_inicio).total_seconds()

    @property
    def tamanho_mb(self) -> float:
        return self.tamanho_bytes / 1024 / 1024

    def to_dict(self) -> IngestaoMetadataDict:
        """Serializa metadados para persistência (DuckDB / Parquet)"""
        return {
            "ano": self.dataset.ano,
            "nome_arquivo": self.dataset.nome_arquivo,
            "url_download": self.dataset.url_download,
            "timestamp_inicio": self.timestamp_inicio.astimezone(timezone.utc).isoformat(),
            "timestamp_fim": self.timestamp_fim.astimezone(timezone.utc).isoformat(),
            "arquivo_destino": str(self.arquivo_destino),
            "tamanho_bytes": self.tamanho_bytes,
            "linhas_ingeridas": self.linhas_ingeridas,
            "checksum_sha256": self.checksum_sha256,
            "status": self.status.value,
            "mensagem_erro": self.mensagem_erro,
            "duracao_segundos": self.duracao_segundos,
            "tamanho_mb": self.tamanho_mb,
        }
"""Domínio lógico do projeto"""

from .contracts import ComparecimentoContrato, IngestaoMetadataDict
from .entities import Dataset
from .enums import StatusIngestao
from .services import (
    construir_metadata_falha,
    construir_metadata_sucesso,
)

__all__ = [
    "ComparecimentoContrato",
    "IngestaoMetadataDict",
    "Dataset",
    "StatusIngestao",
    "construir_metadata_falha",
    "construir_metadata_sucesso",
]

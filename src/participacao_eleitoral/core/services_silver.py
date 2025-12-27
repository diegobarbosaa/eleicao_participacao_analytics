"""Serviços de construção de metadados Silver"""

from datetime import UTC, datetime

from .contracts.ingestao_metadata import IngestaoMetadataDict
from .entities import Dataset
from .enums import StatusIngestao


def construir_metadata_silver_sucesso(
    dataset: Dataset,
    inicio: datetime,
    fim: datetime,
    linhas_antes: int,
    linhas_depois: int,
) -> IngestaoMetadataDict:
    """
    Cria metadata de sucesso da transformação silver.

    Linhas antes = quantidade antes de remover nulos
    Linhas depois = quantidade após transformação final
    """
    return {
        "dataset": dataset.nome,
        "ano": dataset.ano,
        "status": StatusIngestao.SUCESSO.value,
        "inicio": inicio.astimezone(UTC).isoformat(),
        "fim": fim.astimezone(UTC).isoformat(),
        "duracao_segundos": (fim - inicio).total_seconds(),
        "linhas_antes": linhas_antes,
        "linhas_depois": linhas_depois,
        "erro": None,
    }


def construir_metadata_silver_falha(
    dataset: Dataset,
    inicio: datetime,
    fim: datetime,
    erro: str,
) -> IngestaoMetadataDict:
    """Cria metadata de falha da transformação silver."""
    return {
        "dataset": dataset.nome,
        "ano": dataset.ano,
        "status": StatusIngestao.FALHA.value,
        "inicio": inicio.astimezone(UTC).isoformat(),
        "fim": fim.astimezone(UTC).isoformat(),
        "duracao_segundos": (fim - inicio).total_seconds(),
        "linhas_antes": 0,
        "linhas_depois": 0,
        "erro": erro,
    }

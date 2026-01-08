from datetime import UTC, datetime

from .contracts.ingestao_metadata import IngestaoMetadataDict
from .entities import Dataset
from .enums import StatusIngestao


def construir_metadata_sucesso(
    dataset: Dataset,
    inicio: datetime,
    fim: datetime,
    linhas: int,
    tamanho_bytes: int,
    checksum: str,
) -> IngestaoMetadataDict:
    """
    Cria metadata de sucesso.

    Separar isso evita:
    - duplicação
    - inconsistência
    - lógica espalhada
    """

    return {
        "dataset": dataset.nome,
        "ano": dataset.ano,
        "status": StatusIngestao.SUCESSO.value,
        "inicio": inicio.astimezone(UTC).isoformat(),
        "fim": fim.astimezone(UTC).isoformat(),
        "duracao_segundos": (fim - inicio).total_seconds(),
        "linhas": linhas,
        "tamanho_bytes": tamanho_bytes,
        "checksum": checksum,
        "erro": None,
    }


def construir_metadata_falha(
    dataset: Dataset,
    inicio: datetime,
    fim: datetime,
    erro: str,
) -> IngestaoMetadataDict:
    """
    Cria metadata de falha.

    Note que:
    - linhas = 0
    - tamanho = 0
    - checksum vazio
    """

    return {
        "dataset": dataset.nome,
        "ano": dataset.ano,
        "status": StatusIngestao.FALHA.value,
        "inicio": inicio.astimezone(UTC).isoformat(),
        "fim": fim.astimezone(UTC).isoformat(),
        "duracao_segundos": (fim - inicio).total_seconds(),
        "linhas": 0,
        "tamanho_bytes": 0,
        "checksum": "",
        "erro": erro,
    }

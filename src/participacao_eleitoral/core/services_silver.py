"""Serviços de construção de metadados Silver"""

from datetime import UTC, datetime

from participacao_eleitoral.core.contracts.ingestao_metadata import IngestaoMetadataDict
from participacao_eleitoral.core.contracts.silver_metadata import SilverMetadataDict
from participacao_eleitoral.core.entities import Dataset
from participacao_eleitoral.core.enums import StatusIngestao


def construir_metadata_silver_sucesso(
    dataset: Dataset,
    inicio: datetime,
    fim: datetime,
    linhas_antes: int,
    linhas_depois: int,
) -> SilverMetadataDict:
    """
    Cria metadata de sucesso da transformação silver.

    Linhas antes = quantidade antes de remover nulos
    Linhas depois = quantidade após transformação final
    """
    return SilverMetadataDict(
        dataset=dataset.nome,
        ano=dataset.ano,
        status=StatusIngestao.SUCESSO.value,
        inicio=inicio.astimezone(UTC).isoformat(),
        fim=fim.astimezone(UTC).isoformat(),
        duracao_segundos=(fim - inicio).total_seconds(),
        linhas_antes=linhas_antes,
        linhas_depois=linhas_depois,
    )


def construir_metadata_silver_falha(
    dataset: Dataset,
    inicio: datetime,
    fim: datetime,
    erro: str,
) -> IngestaoMetadataDict:
    """Cria metadata de falha da transformação silver."""
    return IngestaoMetadataDict(
        dataset=dataset.nome,
        ano=dataset.ano,
        status=StatusIngestao.FALHA.value,
        inicio=inicio.astimezone(UTC).isoformat(),
        fim=fim.astimezone(UTC).isoformat(),
        duracao_segundos=(fim - inicio).total_seconds(),
        linhas=0,
        tamanho_bytes=0,
        checksum="",
        erro=erro,
    )

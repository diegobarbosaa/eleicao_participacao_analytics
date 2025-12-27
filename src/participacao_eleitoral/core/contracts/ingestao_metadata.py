from typing import TypedDict, NotRequired


class IngestaoMetadataDict(TypedDict, total=False):
    """
    Contrato LÓGICO de metadados de ingestão.

    Usado por:
    - core.services
    - metadata_store
    - Airflow
    """

    dataset: str
    ano: int
    status: str
    inicio: str
    fim: str
    duracao_segundos: float
    linhas: int
    tamanho_bytes: int
    checksum: str
    erro: str | None
    linhas_antes: NotRequired[int]
    linhas_depois: NotRequired[int]

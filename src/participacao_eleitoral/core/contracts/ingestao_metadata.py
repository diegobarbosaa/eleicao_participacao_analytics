from typing import TypedDict


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
    linhas_antes: int
    linhas_depois: int

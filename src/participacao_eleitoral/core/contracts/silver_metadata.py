from typing import TypedDict


class SilverMetadataDict(TypedDict, total=False, total=False):
    """
    Contrato LÓGICO de metadados da camada Silver.

    Usado por:
    - core.services_silver
    - silver.metadata_store
    - Airflow
    """

    dataset: str
    ano: int
    status: str
    inicio: str
    fim: str
    duracao_segundos: float
    linhas_antes: int
    linhas_depois: int
    erro: str | None

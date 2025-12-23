from typing import cast

from participacao_eleitoral.core.contracts.ingestao_metadata import IngestaoMetadataDict
from participacao_eleitoral.ingestion.metadata_store import MetadataStore


def test_metadata_store_persist_and_fetch(tmp_path, settings, logger):
    """
    MetadataStore deve salvar e recuperar metadados.
    """

    store = MetadataStore(
        settings=settings,
        logger=logger,
        db_path=tmp_path / "test.duckdb",
    )

    metadata = {
        "dataset": "comparecimento_abstencao",
        "ano": 2022,
        "status": "sucesso",
        "inicio": "2024-01-01T00:00:00Z",
        "fim": "2024-01-01T00:01:00Z",
        "duracao_segundos": 60.0,
        "linhas": 10,
        "tamanho_bytes": 1000,
        "checksum": "abc",
        "erro": None,
    }

    store.salvar(cast(IngestaoMetadataDict, metadata))
    fetched = store.buscar("comparecimento_abstencao", 2022)

    assert fetched is not None
    assert fetched["status"] == "sucesso"


def test_metadata_store_listar_todos(tmp_path, settings, logger):
    """
    MetadataStore deve listar todas as ingestões.
    """

    store = MetadataStore(
        settings=settings,
        logger=logger,
        db_path=tmp_path / "test.duckdb",
    )

    # Salvar duas ingestões
    metadata1 = {
        "dataset": "comparecimento_abstencao",
        "ano": 2022,
        "status": "sucesso",
        "inicio": "2024-01-01T00:00:00Z",
        "fim": "2024-01-01T00:01:00Z",
        "duracao_segundos": 60.0,
        "linhas": 10,
        "tamanho_bytes": 1000,
        "checksum": "abc",
        "erro": None,
    }

    metadata2 = {
        "dataset": "comparecimento_abstencao",
        "ano": 2020,
        "status": "falha",
        "inicio": "2024-01-01T00:00:00Z",
        "fim": "2024-01-01T00:01:00Z",
        "duracao_segundos": 60.0,
        "linhas": 0,
        "tamanho_bytes": 0,
        "checksum": "",
        "erro": "Erro teste",
    }

    store.salvar(cast(IngestaoMetadataDict, metadata1))
    store.salvar(cast(IngestaoMetadataDict, metadata2))

    todos = store.listar_todos()

    assert len(todos) == 2
    assert todos[0]["ano"] == 2022  # ordenado por ano desc
    assert todos[1]["ano"] == 2020
    assert todos[0]["status"] == "sucesso"
    assert todos[1]["status"] == "falha"

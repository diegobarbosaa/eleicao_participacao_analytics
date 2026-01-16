"""Testes do SilverMetadataStore"""

from participacao_eleitoral.config import Settings
from participacao_eleitoral.silver.metadata_store import SilverMetadataStore


def test_silver_metadata_store_cria_tabela(tmp_path, logger):
    """MetadataStore deve criar tabela ao inicializar."""
    db_path = tmp_path / "test_silver.duckdb"

    settings = Settings()

    store = SilverMetadataStore(settings=settings, logger=logger, db_path=db_path)

    # Verifica se tabela foi criada
    tables = store.conn.execute("SHOW TABLES").fetchall()
    assert ("silver_metadata",) in tables


def test_silver_metadata_store_salvar_e_buscar(tmp_path, logger):
    """MetadataStore deve salvar e buscar metadados."""
    db_path = tmp_path / "test_silver.duckdb"

    settings = Settings()

    store = SilverMetadataStore(settings=settings, logger=logger, db_path=db_path)

    metadata = {
        "dataset": "test_silver",
        "ano": 2022,
        "inicio": "2024-01-01T10:00:00",
        "fim": "2024-01-01T10:05:00",
        "linhas_antes": 1000,
        "linhas_depois": 950,
        "duracao_segundos": 300,
        "status": "SUCESSO",
        "erro": None,
    }

    store.salvar(metadata)

    # Buscar e verificar
    result = store.buscar("test_silver", 2022)
    assert result is not None
    assert result["dataset"] == "test_silver"
    assert result["ano"] == 2022
    assert result["status"] == "SUCESSO"


def test_silver_metadata_store_upsert_idempotencia(tmp_path, logger):
    """MetadataStore deve fazer UPSERT (atualizar se já existe)."""
    db_path = tmp_path / "test_silver.duckdb"

    settings = Settings()

    store = SilverMetadataStore(settings=settings, logger=logger, db_path=db_path)

    # Primeira inserção
    metadata1 = {
        "dataset": "test_silver",
        "ano": 2022,
        "inicio": "2024-01-01T10:00:00",
        "fim": "2024-01-01T10:05:00",
        "linhas_antes": 1000,
        "linhas_depois": 950,
        "duracao_segundos": 300,
        "status": "SUCESSO",
        "erro": None,
    }
    store.salvar(metadata1)

    # Atualização
    metadata2 = {
        "dataset": "test_silver",
        "ano": 2022,
        "inicio": "2024-01-01T10:00:00",
        "fim": "2024-01-01T10:10:00",  # Mudado
        "linhas_antes": 2000,  # Mudado
        "linhas_depois": 1900,  # Mudado
        "duracao_segundos": 600,  # Mudado
        "status": "SUCESSO",
        "erro": None,
    }
    store.salvar(metadata2)

    # Deve haver apenas 1 registro (UPSERT)
    result = store.buscar("test_silver", 2022)
    assert result["duracao_segundos"] == 600  # Valor atualizado

    count = store.conn.execute(
        "SELECT COUNT(*) FROM silver_metadata WHERE dataset = 'test_silver' AND ano = 2022"
    ).fetchone()[0]
    assert count == 1


def test_silver_metadata_store_listar_todos(tmp_path, logger):
    """MetadataStore deve listar todos os metadados."""
    db_path = tmp_path / "test_silver.duckdb"

    settings = Settings()

    store = SilverMetadataStore(settings=settings, logger=logger, db_path=db_path)

    # Inserir múltiplos registros
    for ano in [2022, 2024, 2018]:
        metadata = {
            "dataset": "test_silver",
            "ano": ano,
            "inicio": "2024-01-01T10:00:00",
            "fim": "2024-01-01T10:05:00",
            "linhas_antes": 1000,
            "linhas_depois": 950,
            "duracao_segundos": 300,
            "status": "SUCESSO",
            "erro": None,
        }
        store.salvar(metadata)

    # Listar todos
    results = store.listar_todos()
    assert len(results) == 3

    # Deve estar ordenado por ano DESC
    anos = [r["ano"] for r in results]
    assert anos == [2024, 2022, 2018]


def test_silver_metadata_store_buscar_inexistente(tmp_path, logger):
    """Buscar metadata inexistente deve retornar None."""
    db_path = tmp_path / "test_silver.duckdb"

    settings = Settings()

    store = SilverMetadataStore(settings=settings, logger=logger, db_path=db_path)

    result = store.buscar("dataset_inexistente", 9999)
    assert result is None


def test_silver_metadata_store_falha(tmp_path, logger):
    """MetadataStore deve salvar metadata de falha."""
    db_path = tmp_path / "test_silver.duckdb"

    settings = Settings()

    store = SilverMetadataStore(settings=settings, logger=logger, db_path=db_path)

    metadata = {
        "dataset": "test_silver",
        "ano": 2022,
        "inicio": "2024-01-01T10:00:00",
        "fim": "2024-01-01T10:05:00",
        "linhas_antes": 0,
        "linhas_depois": 0,
        "duracao_segundos": 300,
        "status": "FALHA",
        "erro": "Erro simulado",
    }

    store.salvar(metadata)

    result = store.buscar("test_silver", 2022)
    assert result["status"] == "FALHA"
    assert result["erro"] == "Erro simulado"

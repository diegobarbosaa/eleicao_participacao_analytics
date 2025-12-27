"""Gerencia persistência de metadados de transformação Silver"""

from pathlib import Path
from typing import Any

import duckdb

from participacao_eleitoral.config import Settings
from participacao_eleitoral.utils.logger import ModernLogger


class SilverMetadataStore:
    """
    Gerência persistência de metadados de transformação Silver usando DuckDB.

    Responsabilidades:
    - Garantir idempotência (dataset + ano)
    - Auditar execuções de transformação
    - Servir como fonte de observabilidade do pipeline Silver
    """

    def __init__(
        self,
        settings: Settings,
        logger: ModernLogger,
        db_path: Path | None = None,
    ):
        self.settings = settings
        self.logger = logger

        # Caminho do banco de metadados (silver)
        self.db_path = db_path or self.settings.silver_dir / "_metadata.duckdb"

        # Garante que o diretório existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Conexão DuckDB (arquivo local)
        self.conn = duckdb.connect(str(self.db_path))

        # Inicializa schema
        self._create_tables()

        self.logger.info("silver_metadata_store_inicializado", db_path=str(self.db_path))

    def _create_tables(self) -> None:
        """Inicializa o esquema se não existir."""

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS silver_metadata (
                dataset TEXT NOT NULL,
                ano INTEGER NOT NULL,

                timestamp_inicio TIMESTAMP NOT NULL,
                timestamp_fim TIMESTAMP NOT NULL,

                linhas_antes BIGINT,
                linhas_depois BIGINT,
                duracao_segundos DOUBLE,
                status TEXT,
                erro TEXT,

                PRIMARY KEY (dataset, ano)
            )
            """
        )

    def salvar(self, metadata: dict[str, Any]) -> None:
        """
        Persiste metadados da transformação no DuckDB.

        Usa UPSERT por ano para garantir idempotência.
        """
        self.conn.execute(
            """
            INSERT INTO silver_metadata (
                dataset,
                ano,
                timestamp_inicio,
                timestamp_fim,
                linhas_antes,
                linhas_depois,
                duracao_segundos,
                status,
                erro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (dataset, ano) DO UPDATE SET
                timestamp_inicio = excluded.timestamp_inicio,
                timestamp_fim = excluded.timestamp_fim,
                linhas_antes = excluded.linhas_antes,
                linhas_depois = excluded.linhas_depois,
                duracao_segundos = excluded.duracao_segundos,
                status = excluded.status,
                erro = excluded.erro
            """,
            (
                metadata["dataset"],
                metadata["ano"],
                metadata["inicio"],
                metadata["fim"],
                metadata["linhas_antes"],
                metadata["linhas_depois"],
                metadata["duracao_segundos"],
                metadata["status"],
                metadata["erro"],
            ),
        )

        self.logger.success(
            "silver_metadata_salvo",
            ano=metadata["ano"],
            status=metadata["status"],
        )

    def buscar(self, dataset: str, ano: int) -> dict[str, Any] | None:
        """Busca metadados de uma transformação específica."""

        row = self.conn.execute(
            """
            SELECT *
            FROM silver_metadata
            WHERE dataset = ? AND ano = ?
            """,
            (dataset, ano),
        ).fetchone()

        if not row:
            return None

        columns = [c[0] for c in self.conn.description]
        return dict(zip(columns, row, strict=False))

    def listar_todos(self) -> list[dict[str, Any]]:
        """Lista todas as entradas de metadados de transformação."""

        rows = self.conn.execute(
            """
            SELECT *
            FROM silver_metadata
            ORDER BY ano DESC
            """
        ).fetchall()

        if not rows:
            return []

        columns = [c[0] for c in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in rows]

    def close(self) -> None:
        """Fecha a conexão com o DuckDB."""
        self.conn.close()

    def __enter__(self) -> "SilverMetadataStore":
        """Suporta uso com contexto 'with'."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> bool:
        """Fecha conexão ao sair do contexto."""
        self.close()
        return False  # Não suprimir exceções

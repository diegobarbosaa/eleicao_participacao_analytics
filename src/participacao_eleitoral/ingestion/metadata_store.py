from pathlib import Path

import duckdb

from participacao_eleitoral.config import Settings
from participacao_eleitoral.core.contracts.ingestao_metadata import IngestaoMetadataDict
from participacao_eleitoral.utils.logger import ModernLogger


class MetadataStore:
    """
    Gerencia persistência de metadados de ingestão usando DuckDB.

    Responsabilidades:
    - Garantir idempotência (dataset + ano)
    - Auditar execuções
    - Servir como fonte de observabilidade do pipeline
    """

    def __init__(
        self,
        settings: Settings,
        logger: ModernLogger,
        db_path: Path | None = None,
    ):
        self.settings = settings
        self.logger = logger

        # Caminho do banco de metadados (bronze)
        self.db_path = db_path or self.settings.bronze_dir / "_metadata.duckdb"

        # Garante que o diretório existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Conexão DuckDB (arquivo local)
        self.conn = duckdb.connect(str(self.db_path))

        # Inicializa schema
        self._create_tables()

        self.logger.info("metadata_store_inicializado", db_path=str(self.db_path))

    def _create_tables(self) -> None:
        """
        Inicializa o esquema se não existir.
        """

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingestao_metadata (
                dataset TEXT NOT NULL,
                ano INTEGER NOT NULL,

                timestamp_inicio TIMESTAMP NOT NULL,
                timestamp_fim TIMESTAMP NOT NULL,

                linhas BIGINT,
                tamanho_bytes BIGINT,
                duracao_segundos DOUBLE,
                status TEXT,
                checksum TEXT,
                erro TEXT,

                PRIMARY KEY (dataset, ano)
            )
            """
        )

        # Add missing columns if table already exists (migration)
        self.conn.execute("ALTER TABLE ingestao_metadata ADD COLUMN IF NOT EXISTS status TEXT")
        self.conn.execute("ALTER TABLE ingestao_metadata ADD COLUMN IF NOT EXISTS checksum TEXT")
        self.conn.execute("ALTER TABLE ingestao_metadata ADD COLUMN IF NOT EXISTS erro TEXT")

    def salvar(self, metadata: IngestaoMetadataDict) -> None:
        """
        Persiste metadados da ingestão no DuckDB.

        Usa UPSERT por ano para garantir idempotência."""

        self.conn.execute(
            """
            INSERT INTO ingestao_metadata (
                dataset,
                ano,
                timestamp_inicio,
                timestamp_fim,
                linhas,
                tamanho_bytes,
                duracao_segundos,
                status,
                checksum,
                erro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (dataset, ano) DO UPDATE SET
                timestamp_inicio = excluded.timestamp_inicio,
                timestamp_fim = excluded.timestamp_fim,
                linhas = excluded.linhas,
                tamanho_bytes = excluded.tamanho_bytes,
                duracao_segundos = excluded.duracao_segundos,
                status = excluded.status,
                checksum = excluded.checksum,
                erro = excluded.erro
            """,
            (
                metadata["dataset"],
                metadata["ano"],
                metadata["inicio"],
                metadata["fim"],
                metadata["linhas"],
                metadata["tamanho_bytes"],
                metadata["duracao_segundos"],
                metadata["status"],
                metadata["checksum"],
                metadata["erro"],
            ),
        )

        self.logger.success(
            "metadata_salvo",
            ano=metadata["ano"],
            status=metadata["status"],
        )

    def buscar(self, dataset: str, ano: int) -> dict | None:
        """
        Busca metadados de uma ingestão específica.
        """

        row = self.conn.execute(
            """
            SELECT *
            FROM ingestao_metadata
            WHERE dataset = ? AND ano = ?
            """,
            (dataset, ano),
        ).fetchone()

        if not row:
            return None

        columns = [c[0] for c in self.conn.description]
        return dict(zip(columns, row, strict=False))

    def listar_todos(self) -> list[dict]:
        """
        Lista todas as entradas de metadados de ingestão.

        Returns:
            Lista de dicionários de metadados
        """

        rows = self.conn.execute(
            """
            SELECT *
            FROM ingestao_metadata
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

from pathlib import Path
from typing import Optional

import duckdb

from participacao_eleitoral.ingestion.models import IngestaoMetadata
from participacao_eleitoral.utils.logger import ModernLogger
from participacao_eleitoral.config import Settings


class MetadataStore:
    """Gerencia metadados de ingestão em DuckDB"""

    def __init__(
        self,
        settings: Settings,
        logger: ModernLogger,
        db_path: Optional[Path] = None,
    ):
        self.settings = settings
        self.logger = logger

        self.db_path = db_path or self.settings.bronze_dir / "_metadata.duckdb"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = duckdb.connect(str(self.db_path))
        self._create_tables()

        self.logger.info("metadata_store_inicializado", db_path=str(self.db_path))

    def _create_tables(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ingestao_metadata (
                ano INTEGER PRIMARY KEY,
                nome_arquivo VARCHAR NOT NULL,
                url_download VARCHAR NOT NULL,
                timestamp_inicio VARCHAR NOT NULL,
                timestamp_fim VARCHAR,
                arquivo_destino VARCHAR NOT NULL,
                tamanho_bytes BIGINT,
                linhas_ingeridas BIGINT,
                checksum_sha256 VARCHAR(64),
                status VARCHAR NOT NULL,
                mensagem_erro VARCHAR,
                duracao_segundos DOUBLE
            )
        """)
        self.logger.debug("tabela_metadata_pronta")

    def salvar(self, metadata: IngestaoMetadata) -> None:
        data = metadata.to_dict()

        self.conn.execute("""
            INSERT INTO ingestao_metadata VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT (ano) DO UPDATE SET
                timestamp_fim = excluded.timestamp_fim,
                arquivo_destino = excluded.arquivo_destino,
                tamanho_bytes = excluded.tamanho_bytes,
                linhas_ingeridas = excluded.linhas_ingeridas,
                checksum_sha256 = excluded.checksum_sha256,
                status = excluded.status,
                mensagem_erro = excluded.mensagem_erro,
                duracao_segundos = excluded.duracao_segundos
        """, [
            data["ano"],
            data["nome_arquivo"],
            data["url_download"],
            data["timestamp_inicio"],
            data["timestamp_fim"],
            data["arquivo_destino"],
            data["tamanho_bytes"],
            data["linhas_ingeridas"],
            data["checksum_sha256"],
            data["status"],
            data["mensagem_erro"],
            data["duracao_segundos"],
        ])

        self.logger.success(
            "metadata_salvo",
            ano=data["ano"],
            status=data["status"],
        )

    def buscar_por_ano(self, ano: int) -> Optional[dict]:
        result = self.conn.execute(
            "SELECT * FROM ingestao_metadata WHERE ano = ?",
            [ano],
        ).fetchone()

        if not result:
            return None

        columns = [c[0] for c in self.conn.description]
        return dict(zip(columns, result))

    def listar_todas(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT
                ano,
                timestamp_inicio,
                timestamp_fim,
                duracao_segundos,
                tamanho_bytes,
                linhas_ingeridas,
                status,
                mensagem_erro
            FROM ingestao_metadata
            ORDER BY ano DESC
        """).fetchall()

        if not rows:
            return []

        columns = [c[0] for c in self.conn.description]
        return [dict(zip(columns, row)) for row in rows]

    def close(self) -> None:
        self.conn.close()
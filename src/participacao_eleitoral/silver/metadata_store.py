"""
Gerência persistência de metadados da camada Silver usando DuckDB.

Responsabilidades:
- Garantir idempotência (UPSERT por dataset + ano)
- Auditar execuções de transformação
- Servir como fonte de observabilidade do pipeline Silver
"""
from pathlib import Path
from typing import Any, Optional

import duckdb
from participacao_eleitoral.config import Settings
from participacao_eleitoral.utils.logger import ModernLogger


class SilverMetadataStore:
    """
    Gerência persistência de metadados da camada Silver.
    
    Responsabilidades:
    - Garantir idempotência (UPSERT por dataset + ano)
    - Auditar execuções de transformação
    - Servir como fonte de observabilidade do pipeline Silver
    """

    def __init__(self, settings: Settings, logger: ModernLogger):
        """
        Inicializa a store de metadados.

        Args:
            settings: Instância de Settings
            logger: Logger estruturado para diagnóstico
        """
        self.settings = settings
        self.logger = logger
        # Caminho do banco de metadados (silver)
        self.db_path = settings.silver_dir / "_metadata.duckdb"

    def _inicializa_schema(self) -> None:
        """
        Cria tabela se não existir.

        Returns:
            True: Se criou nova tabela
        """
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS silver_metadata (
                        dataset TEXT NOT NULL,
                        ano INTEGER NOT NULL,
                        timestamp_inicio TIMESTAMP NOT NULL,
                        linhas_antes BIGINT,
                        linhas_depois BIGINT,
                        duracao_segundos DOUBLE,
                        status TEXT,
                        PRIMARY KEY (dataset, ano)
                )
                """)
                self.logger.success("silver_metadata_store_inicializado", db_path=str(self.db_path))
                return None

    def salvar(self, metadata: dict[str, Any]) -> None:
        """
        Salva metadados da transformação no DuckDB.

        Args:
            metadata: Dict[str, Any] com campos e valores
        """
        try:
            columns = ["dataset", "ano", "status", "inicio", "fim", "duracao_segundos", "linhas_antes", "linhas_depois", "checksum", "erro"]
            values = (
                metadata.get("dataset"),
                metadata.get("ano"),
                metadata.get("inicio"),
                metadata.get("fim"),
                metadata.get("duracao_segundos"),
                metadata.get("linhas_antes"),
                metadata.get("linhas_depois"),
                metadata.get("checksum"),
                metadata.get("erro") if metadata.get("erro") else ""
            )

            self.conn.execute(
                f"INSERT INTO silver_metadata ({columns}) VALUES ({values});"
            )

            self.logger.success("silver_metadata_salvo", dataset=metadata["dataset"], ano=metadata["ano"])
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar metadata: {e}", e)
            raise

    def buscar(self, dataset: str, ano: int) -> dict[str, Any] | None:
        """
        Busca metadados de uma transformação específica (dataset + ano).

        Args:
            dataset: Nome do dataset
            ano: Ano da eleição
        """
        try:
            with self.conn:
                row = self.conn.fetchone(
                    f"SELECT * FROM silver_metadata WHERE dataset = ? AND ano = ?"
                    LIMIT 1"
                    f"",
                    (dataset, ano),
                )

            if not row:
                self.logger.error(f"Nenhum registro encontrado com dataset={dataset}, ano={ano}")
                return None

            return {
                "dataset": row["dataset"],
                "ano": row["ano"],
                "status": row["status"],
                "inicio": row["inicio"],
                "fim": row["fim"],
                "duracao_segundos": float(row["duracao_segundos"]),
                "linhas_antes": int(row["linhas_antes"]),
                "linhas_depois": int(row["linhas_depois"]),
                "checksum": row["checksum"],
                "erro": row["erro"] if len(row) > 8 else None,
            }

        except Exception as e:
            self.logger.error(f"Erro ao buscar metadata: {dataset} {dataset}, ano={ano}", e)
            raise

    def listar_todos(self) -> list[dict[str, Any]]:
        """
        Lista todas as entradas de metadados de transformação.

        Returns:
            Lista de dicionários com metadados de transformação.
        """
        try:
            rows = self.conn.fetchall()

            if not rows:
                return []

            rows_dict = [
                {
                    "dataset": str(row["dataset"]),
                    "ano": int(row["ano"]),
                    "status": row["status"],
                    "inicio": row["inicio"],
                    "fim": row["fim"],
                    "duracao_segundos": float(row["duracao_segundos"]),
                    "linhas_antes": int(row["linhas_antes"]),
                    "linhas_depois": int(row["linhas_depois"]),
                    "checksum": row["checksum"],
                    "erro": row["erro"]
                } for row in rows
                ]

        except Exception as e:
            self.logger.error(f"Erro ao listar metadados: {e}", e)
            return []

    def upsert_idempotencia(self, dataset: str, ano: int, linhas_antes: int, linhas_depois: int, 
                              duracao_segundos: float, checksum: str, 
                              erro: str | None) -> bool:
        """
        Atualiza (UPSERT ou cria) metadados se não existirem.

        Retorna:
            True se atualizou, False se foi criação nova.
        """
        try:
            with self.conn:
                result = self.conn.execute(
                    f"INSERT INTO silver_metadata "
                    f"dataset", "ano", "status", "inicio", "fim", 
                    f"linhas_antes", "linhas_depois", "checksum", "erro" "
                    f"ON CONFLICT (dataset, ano) DO UPDATE SET "
                    f"WHERE linhas_antes = ?"
                    )

            row_count = result.fetchone()

            if row_count is None:
                self.logger.warning(f"Conflito de idempotência: {dataset} {dataset}, ano={ano}")
                return False

            else:
                self.logger.info(f"Atualizada com sucesso: {dataset} {dataset}, ano={ano}")
                return True

    def close(self) -> None:
        """Fecha a conexão com o DuckDB."""
        self.conn.close()


    def __enter__(self) -> "SilverMetadataStore":
        """
        Suporta uso com contexto 'with' em métodos do DuckDB.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Fecha conexão ao sair do contexto.

        Suporta uso com contexto 'with' em métodos do DuckDB.
        """
        self.close()
        return None
from pathlib import Path
from typing import Any, Optional
from contextlib import suppress

from duckdb import duckdb
from participacao_eleitoral.config import Settings
from participacao_eleitoral.utils.logger import ModernLogger


class SilverMetadataStore:
    """
    Gerência de metadados da camada Silver.
    
    Responsabilidades:
    - Garantir idempotência (UPSERT por dataset + ano)
    - Auditar execuções de transformação
    - Servir como fonte de observabilidade do pipeline Silver
    """

    def __init__(self, settings: Settings, logger: ModernLogger) -> None:
        """
        Inicializa conexão com DuckDB.
        """
        self.settings = settings
        self.logger = logger
        self.db_path = self.settings.silver_dir / "_metadata.duckdb"

    def salvar(self, dataset: str, ano: int, timestamp_inicio: str, timestamp_fim: str, 
               linhas_antes: int, linhas_depois: int, duracao_segundos: float, 
               checksum: str, erro: str | None) -> None:
        """
        Salva metadados de sucesso da transformação Silver no DuckDB.
        """
        columns = ["dataset", "ano", "status", "inicio", "fim", "duracao_segundos", "linhas_antes", "linhas_depois", "checksum", "erro"]
        
        values = (dataset, ano, "SUCESSO", timestamp_inicio.isoformat(), 
                 timestamp_fim.isoformat(), 
                 duracao_segundos, linhas_antes, linhas_depois, checksum, "")
        
        try:
            with suppress(OSError):
                self.conn.execute(
                    f"INSERT INTO silver_metadata (dataset, ano, status, inicio, fim, duracao_segundos, "
                    f"linhas_antes, linhas_depois, checksum, erro) "
                    f"VALUES ({dataset}, {ano}, {timestamp_inicio}, {timestamp_fim}, {duracao_segundos}, "
                    f"linhas_antes, linhas_depois, checksum, erro})"
                )
                self.logger.success(f"silver_metadata_salvo", dataset=dataset, ano=ano)
        except Exception as e:
            self.logger.error(f"Erro ao salvar metadata Silver: {e}", e)

    def buscar(self, dataset: str, ano: int) -> dict[str, Any] | None:
        """
        Busca metadados de uma transformação específica (dataset + ano).
        """
        try:
            with suppress(OSError):
                row = self.conn.execute(
                    f"SELECT * FROM silver_metadata WHERE dataset = ? AND ano = ?"
                f"LIMIT 1"
                params=(dataset, ano)
                )
        except Exception as e:
            self.logger.error(f"Erro ao buscar metadata: {dataset} {dataset}, ano={ano}", e)
            return None

    def listar_todos(self) -> list[dict[str, Any]]:
        """
        Lista todas as entradas de metadados de transformação.
        """
        try:
            with suppress(OSError):
                rows = self.conn.execute(
                    f"SELECT * FROM silver_metadata ORDER BY ano DESC"
                    )
                return [dict(zip(
                    dataset=str(row["dataset"]),
                    ano=int(row["ano"]),
                    status=row["status"],
                    inicio=row["inicio"],
                    fim=row["fim"],
                    duracao_segundos=float(row["duracao_segundos"]),
                    linhas_antes=int(row["linhas_antes"]),
                    linhas_depois=int(row["linhas_depois"]),
                    checksum=row["checksum"],
                    erro=row["erro"]
                ) for row in rows
                )
        except Exception as e:
            self.logger.error(f"Erro ao listar metadados: {e}", e)
            return []

    def upsert_idempotencia(self, dataset: str, ano: int,
                              linhas_antes: int, linhas_depois: int, 
                              duracao_segundos: float, checksum: str) -> bool:
        """
        Atualiza (UPSERT ou cria) metadados se não existirem.
        
        Retorna True se atualizou, False se foi criação nova.
        """
        try:
            with suppress(OSError):
            result = self.conn.execute(
                f"INSERT INTO silver_metadata "
                f"(dataset, ano, status, inicio, fim, duracao_segundos, "
                f"linhas_antes, linhas_depois, checksum, erro) "
                f") "
                f"ON CONFLICT (dataset, ano) DO UPDATE SET "
                f"WHERE linhas_antes = ?"
                )
            )
            count = result.rowcount
            if count == 0:
                self.logger.info(f"Nenhum registro encontrado com dataset={dataset}, ano={ano}")
                return True
            else:
                self.logger.warning(f"Conflito de idempotência: {dataset={dataset}, ano={ano}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar idempotência: {e}", e)
            return False

    def _inicializa_tabela(self) -> None:
        """
        Inicializa tabela no DuckDB se não existir.
        """
        with suppress(OSError):
            self.conn.execute(
                f"CREATE TABLE IF NOT EXISTS silver_metadata ("
                f"dataset TEXT, "
                f"ano INTEGER NOT NULL,"
                f"linhas_antes BIGINT,"
                f"linhas_depois BIGINT,"
                f"duracao_segundos DOUBLE,"
                f"status TEXT,"
                f"erro TEXT,"
                f"PRIMARY KEY (dataset, ano)"
                f")"
            )

        return
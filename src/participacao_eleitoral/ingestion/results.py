from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DownloadResult:
    """
    Resultado do download de um dataset.

    Este objeto:
    - é imutável (frozen=True)
    - representa download bem-sucedido
    - contém todas as informações necessárias para próximos passos
    """

    # Caminho final do CSV (já extraído se veio ZIP)
    csv_path: Path

    # Tamanho total do arquivo em bytes
    tamanho_bytes: int

    # Checksum SHA-256 do CSV final
    checksum_sha256: str


@dataclass(frozen=True)
class ConvertResult:
    """
    Resultado da conversão CSV → Parquet.

    Separar isso ajuda:
    - clareza
    - testes
    - uso no Airflow
    """

    # Caminho final do Parquet
    parquet_path: Path

    # Quantidade de linhas escritas
    linhas: int

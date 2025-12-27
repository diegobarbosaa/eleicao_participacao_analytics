"""Objetos de resultado da transformação Silver"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SilverTransformResult:
    """
    Resultado da transformação Bronze → Silver.

    Este objeto:
    - é imutável (frozen=True)
    - representa transformação bem-sucedida
    - contém informações necessárias para próximos passos
    """

    silver_path: Path
    linhas: int

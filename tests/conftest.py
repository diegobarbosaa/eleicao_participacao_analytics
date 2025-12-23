from pathlib import Path

import pytest

from participacao_eleitoral.config import Settings
from participacao_eleitoral.utils.logger import ModernLogger


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """
    Fixture global de Settings para testes.

    Usa diretórios temporários para garantir:
    - isolamento entre testes
    - nenhum dado real sendo sobrescrito
    """

    settings = Settings()

    # Redireciona paths para ambiente temporário
    settings.data_dir = tmp_path / "data"
    settings.bronze_dir = settings.data_dir / "bronze"
    settings.silver_dir = settings.data_dir / "silver"
    settings.gold_dir = settings.data_dir / "gold"
    settings.logs_dir = tmp_path / "logs"

    # Garante que os diretórios existam
    settings.bronze_dir.mkdir(parents=True, exist_ok=True)
    settings.silver_dir.mkdir(parents=True, exist_ok=True)
    settings.gold_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    return settings

@pytest.fixture
def logger() -> ModernLogger:
    """
    Fixture de logger para testes.

    Usa nível DEBUG para facilitar diagnóstico
    e não escreve em arquivos reais.
    """

    return ModernLogger(level="DEBUG")

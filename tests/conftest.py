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

    # Criar diretórios temporários manualmente
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "bronze").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "silver").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "gold").mkdir(parents=True, exist_ok=True)
    (tmp_path / "logs").mkdir(parents=True, exist_ok=True)

    return Settings()


@pytest.fixture
def logger() -> ModernLogger:
    """
    Fixture de logger para testes.

    Usa nível DEBUG para facilitar diagnóstico
    e não escreve em arquivos reais.
    """

    return ModernLogger(level="DEBUG")

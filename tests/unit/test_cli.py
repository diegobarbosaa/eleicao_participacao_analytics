"""Testes para CLI corrigida."""

import subprocess
import sys


def test_cli_help_principal() -> None:
    """Testa se help principal mostra estrutura correta."""
    result = subprocess.run(
        [sys.executable, "-m", "participacao_eleitoral", "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "data" in result.stdout
    assert "validate" in result.stdout
    assert "utils" in result.stdout


def test_cli_data_help() -> None:
    """Testa help do subcomando data."""
    result = subprocess.run(
        [sys.executable, "-m", "participacao_eleitoral", "data", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ingest" in result.stdout
    assert "list-years" in result.stdout


# Teste removido pois a opção de recursos experimentais testada era código morto não usado


def test_cli_utils_version() -> None:
    """Testa comando utils version."""
    result = subprocess.run(
        [sys.executable, "-m", "participacao_eleitoral", "utils", "version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "v1.0.0" in result.stdout


# Teste removido pois a exibição de recursos experimentais testada era código morto não usado


def test_cli_data_list_years() -> None:
    """Testa comando data list-years."""
    result = subprocess.run(
        [sys.executable, "-m", "participacao_eleitoral", "data", "list-years"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Anos disponíveis:" in result.stdout
    assert "2024" in result.stdout
    assert "2022" in result.stdout

"""Testes de configuração do projeto para verificar validação de valores."""

import pytest

from participacao_eleitoral.config import Settings


def test_settings_default_log_level() -> None:
    """Settings deve usar INFO como padrão."""
    settings = Settings()
    assert settings.log_level == "INFO"


def test_settings_default_retries() -> None:
    """Settings deve ter 3 retries como padrão."""
    settings = Settings()
    assert settings.max_retries == 3


def test_settings_default_timeout() -> None:
    """Settings deve ter 300 segundos de timeout padrão."""
    settings = Settings()
    assert settings.request_timeout == 300


def test_settings_data_dir() -> None:
    """Settings deve ter diretório de dados configurado."""
    settings = Settings()
    settings.setup_dirs()
    assert settings.data_dir.exists()


def test_settings_bronze_dir() -> None:
    """Settings deve ter diretório bronze configurado."""
    settings = Settings()
    settings.setup_dirs()
    assert settings.bronze_dir.exists()


def test_settings_silver_dir() -> None:
    """Settings deve ter diretório silver configurado."""
    settings = Settings()
    settings.setup_dirs()
    assert settings.silver_dir.exists()


def test_settings_gold_dir() -> None:
    """Settings deve ter diretório gold configurado."""
    settings = Settings()
    settings.setup_dirs()
    assert settings.gold_dir.exists()


def test_settings_tse_base_url() -> None:
    """Settings deve ter URL base do TSE configurada."""
    settings = Settings()
    assert settings.tse_base_url.startswith("https://")
    assert ".tse.jus.br" in settings.tse_base_url


def test_settings_invalid_tse_base_url() -> None:
    """Settings deve rejeitar URL inválida."""
    with pytest.raises(ValueError, match="URL must be HTTP or HTTPS"):
        Settings(tse_base_url="ftp://invalid.url")


def test_settings_invalid_tse_base_url_protocol() -> None:
    """Settings deve rejeitar URL sem protocolo."""
    with pytest.raises(ValueError, match="Invalid URL"):
        Settings(tse_base_url="tse.jus.br")


def test_settings_invalid_tse_base_url_missing_prefix() -> None:
    """Settings deve rejeitar URL vazia."""
    with pytest.raises(ValueError, match="Invalid URL"):
        Settings(tse_base_url="")


def test_settings_log_levels() -> None:
    """Todos os níveis de log devem ser aceitos."""
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        settings = Settings(log_level=level)  # type: ignore[arg-type]
        assert settings.log_level == level


def test_settings_request_timeout_range() -> None:
    """Timeout deve estar entre 10 e 3600 segundos."""
    settings = Settings()
    assert 10 <= settings.request_timeout <= 3600


def test_settings_max_retries_range() -> None:
    """Retries deve estar entre 1 e 10."""
    settings = Settings()
    assert 1 <= settings.max_retries <= 10


def test_settings_chunk_size() -> None:
    """Chunk size deve ser positivo e suficiente."""
    settings = Settings()
    assert settings.chunk_size >= 1024


def test_settings_polars_threads() -> None:
    """Threads do Polars deve usar todos os CPUs disponíveis."""
    settings = Settings()
    assert settings.polars_threads >= 1


def test_settings_enable_validation_flags_removed() -> None:
    """Feature flags de validação foram removidas."""
    settings = Settings()
    assert not hasattr(settings, "enable_strict_validation")
    assert not hasattr(settings, "enable_performance_logging")

"""Testes adicionais para o Logger para aumentar cobertura"""

import json

from participacao_eleitoral.utils.logger import ModernLogger


def test_logger_bind_context() -> None:
    """
    Logger deve ser capaz de fazer bind de contexto.
    """
    logger1 = ModernLogger(level="DEBUG")
    logger2 = logger1.bind(usuario="test", ano=2022)

    assert logger2.context == {"usuario": "test", "ano": 2022}
    assert logger1.context == {}


def test_logger_should_log() -> None:
    """
    Logger deve respeitar nível de log configurado.
    """
    logger = ModernLogger(level="WARNING")

    # WARNING e acima devem ser logados
    assert logger._should_log("WARNING") is True
    assert logger._should_log("ERROR") is True
    assert logger._should_log("CRITICAL") is True

    # INFO e DEBUG não devem ser logados
    assert logger._should_log("INFO") is False
    assert logger._should_log("DEBUG") is False

    # SUCCESS mesmo nível de INFO
    assert logger._should_log("SUCCESS") is False


def test_logger_format_value_inteiro_grande() -> None:
    """
    Logger deve formatar inteiros grandes com separador de milhar.
    """
    logger = ModernLogger()
    result = logger._format_value("quantidade", 1234567)
    assert result == "1,234,567"


def test_logger_format_value_float() -> None:
    """
    Logger deve formatar floats com 2 casas decimais.
    """
    logger = ModernLogger()
    result = logger._format_value("valor", 3.14159)
    assert result == "3.14"


def test_logger_format_value_bool() -> None:
    """
    Logger deve formatar booleans como checkmarks.
    """
    logger = ModernLogger()

    assert logger._format_value("status", True) == "✓"
    assert logger._format_value("status", False) == "✗"


def test_logger_format_value_ano() -> None:
    """
    Logger deve formatar anos sem separador.
    """
    logger = ModernLogger()
    result = logger._format_value("ano", 2022)
    assert result == "2022"


def test_logger_format_context() -> None:
    """
    Logger deve formatar contexto corretamente.
    """
    logger = ModernLogger()
    result = logger._format_context(ano=2022, linhas=1000, status=True)
    assert "ano=2022" in result
    assert "linhas=1,000" in result
    assert "status=✓" in result


def test_logger_detecta_airflow(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """
    Logger deve detectar quando está rodando no Airflow.
    """
    # Sem variável de ambiente
    logger = ModernLogger()
    assert logger.is_airflow is False

    # Com variável de ambiente
    monkeypatch.setenv("AIRFLOW_CTX_DAG_ID", "test_dag")
    logger2 = ModernLogger()
    assert logger2.is_airflow is True


def test_logger_escreve_arquivo(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """
    Logger deve escrever logs em arquivo quando configurado.
    """
    log_file = tmp_path / "test.log"
    logger = ModernLogger(level="INFO", log_file=str(log_file))

    logger.info("mensagem teste", ano=2022)

    # Verificar arquivo existe
    assert log_file.exists()

    # Verificar conteúdo é JSON válido
    content = log_file.read_text()
    log_entry = json.loads(content)

    assert log_entry["level"] == "INFO"
    assert log_entry["message"] == "mensagem teste"
    assert log_entry["context"] == {"ano": 2022}
    assert "timestamp" in log_entry


def test_logger_nao_escreve_arquivo_se_nao_configurado(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """
    Logger não deve criar arquivo se não configurado.
    """
    log_file = tmp_path / "test.log"
    logger = ModernLogger(level="INFO", log_file=None)

    logger.info("mensagem teste")

    # Verificar arquivo NÃO existe
    assert not log_file.exists()


def test_logger_falha_graciosamente_ao_escrever_arquivo(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """
    Logger deve falhar graciosamente se não conseguir escrever em arquivo.
    """
    # Usar caminho inválido
    logger = ModernLogger(level="INFO", log_file="/caminho/impossivel/test.log")

    # Não deve levantar erro
    logger.info("mensagem teste")


def test_logger_niveis_disponiveis() -> None:
    """
    Logger deve ter todos os níveis de log definidos.
    """
    assert "DEBUG" in ModernLogger.LEVELS
    assert "INFO" in ModernLogger.LEVELS
    assert "SUCCESS" in ModernLogger.LEVELS
    assert "WARNING" in ModernLogger.LEVELS
    assert "ERROR" in ModernLogger.LEVELS
    assert "CRITICAL" in ModernLogger.LEVELS
    assert "PROGRESS" in ModernLogger.LEVELS

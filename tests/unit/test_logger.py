"""Testes para o logger."""

from participacao_eleitoral.utils.logger import ModernLogger


class TestModernLogger:
    """Testa funcionalidade do logger."""
    
    def test_criar_logger(self):
        """Testa criação de logger."""
        logger = ModernLogger()
        
        assert logger is not None
        assert logger.show_timestamp is False
    
    def test_format_value_ano(self):
        """Testa que ano não tem vírgula."""
        logger = ModernLogger()
        
        # Ano não deve ter separador de milhar
        formatted = logger._format_value("ano", 2024)
        assert formatted == "2024"
        assert "," not in formatted
    
    def test_format_value_linhas(self):
        """Testa que números grandes têm vírgula."""
        logger = ModernLogger()
        
        # Linhas devem ter separador
        formatted = logger._format_value("linhas", 9825477)
        assert "," in formatted
        assert formatted == "9,825,477"
    
    def test_format_value_float(self):
        """Testa formatação de float."""
        logger = ModernLogger()
        
        # ✅ CORRIGIR: Logger usa 2 casas decimais (.2f)
        formatted = logger._format_value("tamanho", 65.28)
        assert formatted == "65.28"  # 2 casas decimais
        
        # Testar arredondamento
        formatted2 = logger._format_value("tamanho", 65.2)
        assert formatted2 == "65.20"

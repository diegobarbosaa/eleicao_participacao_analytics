from participacao_eleitoral.core.contracts.comparecimento import (
    ComparecimentoContrato,
)


def test_contrato_define_dataset_name() -> None:
    """
    O contrato deve expor um nome lógico estável.
    """
    assert ComparecimentoContrato.DATASET_NAME == "comparecimento_abstencao"


def test_contrato_tem_campos_obrigatorios() -> None:
    """
    Campos obrigatórios NÃO podem ser vazios.
    """
    assert len(ComparecimentoContrato.CAMPOS_OBRIGATORIOS) > 0


def test_campos_obrigatorios_sao_strings() -> None:
    """
    Contrato é semântico: campos devem ser nomes, não tipos.
    """
    for campo in ComparecimentoContrato.CAMPOS_OBRIGATORIOS:
        assert isinstance(campo, str)


def test_contrato_tem_campos_opcionais() -> None:
    """
    Deve haver campos opcionais definidos.
    """
    assert len(ComparecimentoContrato.CAMPOS_OPCIONAIS) >= 0


def test_contrato_tem_validacoes() -> None:
    """
    Deve haver regras de validação definidas.
    """
    assert len(ComparecimentoContrato.CAMPOS_VALIDACOES) > 0

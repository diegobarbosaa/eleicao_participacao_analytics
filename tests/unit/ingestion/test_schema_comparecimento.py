from participacao_eleitoral.ingestion.schemas.comparecimento import (
    SCHEMA_COMPARECIMENTO,
    validar_schema_contra_contrato,
)


def test_schema_respeita_contrato() -> None:
    """
    Schema físico deve respeitar o contrato lógico.
    """
    validar_schema_contra_contrato()


def test_schema_nao_vazio() -> None:
    """
    Schema não pode ser vazio.
    """
    assert len(SCHEMA_COMPARECIMENTO) > 0

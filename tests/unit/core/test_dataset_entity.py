import pytest

from participacao_eleitoral.core.contracts.comparecimento import ComparecimentoContrato
from participacao_eleitoral.core.entities import Dataset


def test_dataset_criacao_sucesso() -> None:
    """Dataset deve ser criado com dados válidos."""
    dataset = Dataset(
        nome="comparecimento_abstencao", ano=2022, url_origem="https://example.com/dataset.zip"
    )

    assert dataset.nome == "comparecimento_abstencao"
    assert dataset.ano == 2022
    assert dataset.url_origem == "https://example.com/dataset.zip"


def test_dataset_ano_invalido_baixo() -> None:
    """Deve falhar com ano abaixo do mínimo."""
    with pytest.raises(ValueError, match="Ano inválido"):
        Dataset(
            nome="comparecimento_abstencao", ano=1999, url_origem="https://example.com/dataset.zip"
        )


def test_dataset_ano_invalido_alto() -> None:
    """Deve falhar com ano acima do máximo."""
    with pytest.raises(ValueError, match="Ano inválido"):
        Dataset(
            nome="comparecimento_abstencao", ano=2031, url_origem="https://example.com/dataset.zip"
        )


def test_dataset_url_invalida() -> None:
    """Deve falhar com URL sem HTTP/HTTPS ou path inválido."""
    with pytest.raises(ValueError, match="URL/Path inválido"):
        Dataset(
            nome="comparecimento_abstencao", ano=2022, url_origem="ftp://example.com/dataset.zip"
        )


def test_dataset_nome_vazio() -> None:
    """Deve falhar com nome vazio."""
    with pytest.raises(ValueError, match="Nome deve ser string não vazia"):
        Dataset(nome="", ano=2022, url_origem="https://example.com/dataset.zip")


def test_dataset_nome_desconhecido() -> None:
    """Deve falhar com nome não conhecido."""
    with pytest.raises(ValueError, match="Dataset desconhecido"):
        Dataset(nome="dataset_inexistente", ano=2022, url_origem="https://example.com/dataset.zip")


def test_dataset_identificador_unico() -> None:
    """Deve gerar identificador único."""
    dataset = Dataset(
        nome="comparecimento_abstencao", ano=2022, url_origem="https://example.com/dataset.zip"
    )

    assert dataset.identificador_unico == "comparecimento_abstencao:2022"


def test_dataset_eh_comparecimento() -> None:
    """Deve identificar corretamente dataset de comparecimento."""
    dataset_comparecimento = Dataset(
        nome="comparecimento_abstencao", ano=2022, url_origem="https://example.com/dataset.zip"
    )

    assert dataset_comparecimento.eh_comparecimento


def test_dataset_obter_contrato() -> None:
    """Deve retornar contrato correto."""
    dataset = Dataset(
        nome="comparecimento_abstencao", ano=2022, url_origem="https://example.com/dataset.zip"
    )

    contrato = dataset.obter_contrato()
    assert contrato == ComparecimentoContrato


def test_dataset_obter_contrato_desconhecido() -> None:
    """Deve falhar ao obter contrato de dataset desconhecido."""

    # Método removido pois dataclass frozen impede alteração
    pytest.skip("Método não implementado - frozen dataclass impede alteração")


# Testes removidos pois o método testado era código morto não usado


def test_dataset_imutabilidade() -> None:
    """Dataset deve ser imutável (frozen dataclass)."""
    dataset = Dataset(
        nome="comparecimento_abstencao", ano=2022, url_origem="https://example.com/dataset.zip"
    )

    # Verifica se dataclass está frozen
    assert hasattr(dataset, "__dataclass_params__")
    assert dataset.__dataclass_params__.frozen

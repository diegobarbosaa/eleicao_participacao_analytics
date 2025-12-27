"""Contratos da camada Silver"""

from typing import Any, ClassVar


class ComparecimentoSilverContrato:
    """
    CONTRATO LÓGICO do dataset de comparecimento eleitoral na camada Silver.

    Diferenças da camada Bronze:
    - Campos calculados (taxas de participação)
    - Dados padronizados
    - Regiões mapeadas
    - Validações adicionais
    """

    DATASET_NAME: ClassVar[str] = "comparecimento_abstencao_silver"

    # Campos da camada bronze (mantidos)
    CAMPOS_BRONZE: ClassVar[list[str]] = [
        "ANO_ELEICAO",
        "CD_MUNICIPIO",
        "NM_MUNICIPIO",
        "SG_UF",
        "QT_APTOS",
        "QT_COMPARECIMENTO",
        "QT_ABSTENCAO",
    ]

    # Campos novos da camada silver
    CAMPOS_SILVER: ClassVar[list[str]] = [
        "TAXA_COMPARECIMENTO_PCT",
        "TAXA_ABSTENCAO_PCT",
        "NOME_REGIAO",
    ]

    # Todos os campos obrigatórios
    CAMPOS_OBRIGATORIOS: ClassVar[list[str]] = CAMPOS_BRONZE + CAMPOS_SILVER

    # Validações específicas Silver
    CAMPOS_VALIDACOES: ClassVar[dict[str, dict[str, Any]]] = {
        "TAXA_COMPARECIMENTO_PCT": {
            "tipo": "decimal",
            "minimo": 0,
            "maximo": 100,
            "descricao": "Taxa de comparecimento em percentual",
        },
        "TAXA_ABSTENCAO_PCT": {
            "tipo": "decimal",
            "minimo": 0,
            "maximo": 100,
            "descricao": "Taxa de abstenção em percentual",
        },
        "NOME_REGIAO": {
            "tipo": "texto",
            "descricao": "Região geográfica baseada na UF",
        },
    }

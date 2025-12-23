# ClassVar indica que o atributo pertence à CLASSE,
# e não às instâncias.
#
# Aqui isso é fundamental porque:
# - não queremos criar objetos dessa classe
# - queremos usar a classe como um "namespace" de contrato
from typing import Any, ClassVar


class ComparecimentoContrato:
    """
    CONTRATO LÓGICO do dataset de comparecimento eleitoral.

    Este arquivo define:
    - quais campos o dataset DEVE ter
    - quais campos podem existir opcionalmente

    Ele NÃO define:
    - tipos físicos (Int32, Utf8, etc.)
    - formato de arquivo (CSV, Parquet)
    - biblioteca de leitura (Polars)

    Ou seja: isso é DOMÍNIO PURO.
    """

    # Identificador lógico e estável do dataset.
    #
    # Esse nome:
    # - é usado em metadados
    # - pode ser usado no pipeline
    # - pode ser usado no Superset
    #
    # Se amanhã o CSV mudar de nome, isso NÃO muda.
    DATASET_NAME: ClassVar[str] = "comparecimento_abstencao"

    # Lista de campos que são OBRIGATÓRIOS para o domínio.
    #
    # Se qualquer um desses campos não existir:
    # - o dataset perde significado analítico
    # - a ingestão deve FALHAR
    #
    # Note que aqui só falamos de NOMES e SIGNIFICADO,
    # não de tipos ou parsing.
    CAMPOS_OBRIGATORIOS: ClassVar[list[str]] = [
        "ANO_ELEICAO",  # ano do pleito (dimensão temporal)
        "CD_MUNICIPIO",  # identificador único do município
        "NM_MUNICIPIO",  # nome do município (dimensão)
        "SG_UF",  # estado (dimensão geográfica)
        "QT_APTOS",  # eleitores aptos (métrica base)
        "QT_COMPARECIMENTO",  # eleitores que votaram
        "QT_ABSTENCOES",  # eleitores que se abstiveram
    ]

    # Campos que podem existir, mas não são críticos.
    #
    # A ausência desses campos:
    # - NÃO quebra o domínio
    # - NÃO invalida análises principais
    #
    # Eles normalmente servem para:
    # - análises mais detalhadas
    # - filtros adicionais
    CAMPOS_OPCIONAIS: ClassVar[list[str]] = [
        "NR_ZONA",  # zona eleitoral
        "NR_TURNO",  # turno da eleição
        "NM_UF",  # nome completo do estado
    ]

    # Regras de validação por campo (regras de negócio)
    #
    # Define validações que os dados devem satisfazer:
    # - tipos (semântico, não físico)
    # - restrições de valor
    # - relações entre campos
    CAMPOS_VALIDACOES: ClassVar[dict[str, dict[str, Any]]] = {
        "ANO_ELEICAO": {
            "tipo": "inteiro",
            "minimo": 2000,
            "maximo": 2030,
            "descricao": "Ano do pleito eleitoral",
        },
        "CD_MUNICIPIO": {"tipo": "inteiro", "minimo": 1, "descricao": "Código IBGE do município"},
        "NM_MUNICIPIO": {"tipo": "texto", "nao_vazio": True, "descricao": "Nome do município"},
        "SG_UF": {"tipo": "texto", "tamanho": 2, "descricao": "Sigla da unidade federativa"},
        "QT_APTOS": {"tipo": "inteiro", "minimo": 0, "descricao": "Quantidade de eleitores aptos"},
        "QT_COMPARECIMENTO": {
            "tipo": "inteiro",
            "minimo": 0,
            "descricao": "Quantidade de eleitores que compareceram",
        },
        "QT_ABSTENCOES": {"tipo": "inteiro", "minimo": 0, "descricao": "Quantidade de abstenções"},
    }


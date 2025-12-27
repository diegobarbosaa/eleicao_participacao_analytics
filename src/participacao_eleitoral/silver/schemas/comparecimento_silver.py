"""Schema físico da camada Silver"""

import polars as pl

from participacao_eleitoral.core.contracts.comparecimento_silver import (
    ComparecimentoSilverContrato,
)

SCHEMA_SILVER = {
    # Campos bronze (mantidos)
    "ANO_ELEICAO": pl.Int32,
    "CD_MUNICIPIO": pl.Int32,
    "NM_MUNICIPIO": pl.Utf8,
    "SG_UF": pl.Utf8,
    "QT_APTOS": pl.Int64,
    "QT_COMPARECIMENTO": pl.Int64,
    "QT_ABSTENCAO": pl.Int64,
    # Campos silver (novos)
    "TAXA_COMPARECIMENTO_PCT": pl.Float64,
    "TAXA_ABSTENCAO_PCT": pl.Float64,
    "NOME_REGIAO": pl.Utf8,
}

# Mapeamento de tipos lógicos (contrato) → tipos Polars físicos válidos
# Isso permite validar se o schema físico respeita as regras de negócio
LOGICO_PHYSICO_MAP: dict[str, tuple[type[pl.DataType], ...]] = {
    "inteiro": (
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.Int64,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.UInt64,
    ),
    "texto": (pl.Utf8, pl.Categorical),
    "decimal": (pl.Float32, pl.Float64),
}


def validar_schema_silver_contra_contrato() -> None:
    """
    Garante que o schema físico atende o contrato lógico.

    Essa função protege o domínio contra:
    - mudanças silenciosas no schema
    - transformações inconsistentes
    - erros que só apareceriam no BI
    """

    # Validação 1: Campos obrigatórios (existência)
    campos_schema = set(SCHEMA_SILVER.keys())
    campos_contrato = set(ComparecimentoSilverContrato.CAMPOS_OBRIGATORIOS)

    faltantes = campos_contrato - campos_schema

    if faltantes:
        raise RuntimeError(
            f"Schema físico Silver não atende contrato lógico. Campos faltantes: {faltantes}"
        )

    # Validação 2: Tipos de campos obrigatórios
    # Verifica se o tipo físico respeita o tipo lógico definido no contrato
    for campo in campos_contrato:
        if campo in ComparecimentoSilverContrato.CAMPOS_VALIDACOES:
            tipo_logico = ComparecimentoSilverContrato.CAMPOS_VALIDACOES[campo]["tipo"]
            tipo_fisico = SCHEMA_SILVER[campo]

            # Buscar tipos válidos para o tipo lógico
            tipos_validos = LOGICO_PHYSICO_MAP.get(tipo_logico, ())

            if tipo_fisico not in tipos_validos:
                raise RuntimeError(
                    f"Schema físico Silver não atende contrato lógico. "
                    f"Campo '{campo}' tem tipo físico {tipo_fisico.__name__} "
                    f"mas contrato espera tipo lógico '{tipo_logico}'. "
                    f"Tipos válidos: {[t.__name__ for t in tipos_validos]}"
                )

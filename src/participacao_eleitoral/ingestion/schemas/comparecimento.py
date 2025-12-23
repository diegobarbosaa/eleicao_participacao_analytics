# Polars é usado APENAS aqui porque:
# - isso é infraestrutura
# - estamos definindo como o dado será lido fisicamente
import polars as pl

# Importamos o contrato lógico do core
# para VALIDAR se o schema físico respeita o domínio.
#
# Importante:
# - ingestion depende do core
# - core NÃO depende de ingestion
from participacao_eleitoral.core.contracts.comparecimento import (
    ComparecimentoContrato,
)

# SCHEMA FÍSICO de leitura do CSV usando Polars.
#
# Aqui definimos:
# - tipo físico de cada coluna
# - como o CSV deve ser interpretado
#
# Este schema:
# - melhora performance
# - evita inferência errada
# - falha cedo se o CSV mudar
SCHEMA_COMPARECIMENTO = {
    "ANO_ELEICAO": pl.Int32,          # ano cabe em Int32
    "CD_MUNICIPIO": pl.Int32,         # código numérico do município
    "NM_MUNICIPIO": pl.Utf8,          # texto
    "SG_UF": pl.Utf8,                 # sigla do estado
    "QT_APTOS": pl.Int64,             # números grandes → Int64
    "QT_COMPARECIMENTO": pl.Int64,
    "QT_ABSTENCOES": pl.Int64,
    "NR_ZONA": pl.Int32,              # opcional
    "NR_TURNO": pl.Int8,              # poucos valores possíveis
    "NM_UF": pl.Utf8,                 # opcional
}

def validar_schema_contra_contrato() -> None:
    """
    Garante que o schema físico atende o contrato lógico.

    Essa função protege o domínio contra:
    - mudanças silenciosas no CSV
    - ingestões inconsistentes
    - erros que só apareceriam no BI
    """

    # Conjunto de colunas definidas no schema físico
    campos_schema = set(SCHEMA_COMPARECIMENTO.keys())

    # Conjunto de colunas obrigatórias do domínio
    campos_contrato = set(ComparecimentoContrato.CAMPOS_OBRIGATORIOS)

    # Calcula quais campos obrigatórios
    # NÃO estão presentes no schema físico
    faltantes = campos_contrato - campos_schema

    # Se houver qualquer campo obrigatório faltando,
    # falhamos imediatamente.
    #
    # Isso é uma decisão arquitetural:
    # preferimos falhar cedo do que ingerir dado errado.
    if faltantes:
        raise RuntimeError(
            f"Schema físico não atende contrato lógico. "
            f"Campos faltantes: {faltantes}"
        )

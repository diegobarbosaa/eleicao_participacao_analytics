"""Testes de validação de schema Silver"""

from participacao_eleitoral.silver.schemas.comparecimento_silver import (
    SCHEMA_SILVER,
    validar_schema_silver_contra_contrato,
)


def test_schema_silver_contem_campos_obrigatorios():
    """Schema físico Silver deve conter todos os campos obrigatórios do contrato."""
    campos_schema = set(SCHEMA_SILVER.keys())

    from participacao_eleitoral.core.contracts.comparecimento_silver import (
        ComparecimentoSilverContrato,
    )

    campos_contrato = set(ComparecimentoSilverContrato.CAMPOS_OBRIGATORIOS)

    # Todos os campos do contrato devem estar no schema
    assert campos_contrato.issubset(campos_schema)


def test_schema_silver_contem_tipos_polars():
    """Schema físico Silver deve usar tipos Polars válidos."""
    import polars as pl

    for campo, tipo in SCHEMA_SILVER.items():
        assert tipo in [
            pl.Int32,
            pl.Int64,
            pl.Utf8,
            pl.Float64,
        ], f"Campo {campo} tem tipo inválido: {tipo}"


def test_validar_schema_silver_contra_contrato():
    """Validação deve passar com schema correto."""
    # Este teste verifica que a validação não levanta erro
    # com o schema atual
    validar_schema_silver_contra_contrato()  # Não deve levantar erro


def test_schema_silver_campos_novos_taxas():
    """Schema Silver deve conter campos calculados (taxas)."""
    assert "TAXA_COMPARECIMENTO_PCT" in SCHEMA_SILVER
    assert "TAXA_ABSTENCAO_PCT" in SCHEMA_SILVER


def test_schema_silver_campos_novos_regiao():
    """Schema Silver deve conter campo de região geográfica."""
    assert "NOME_REGIAO" in SCHEMA_SILVER


def test_schema_silver_mantem_campos_bronze():
    """Schema Silver deve manter todos os campos Bronze."""
    campos_bronze = [
        "ANO_ELEICAO",
        "CD_MUNICIPIO",
        "NM_MUNICIPIO",
        "SG_UF",
        "QT_APTOS",
        "QT_COMPARECIMENTO",
        "QT_ABSTENCAO",
    ]

    for campo in campos_bronze:
        assert campo in SCHEMA_SILVER


def test_schema_silver_tipos_corretos():
    """Schema Silver deve ter tipos corretos para cada campo."""
    import polars as pl

    # Campos numéricos
    assert SCHEMA_SILVER["ANO_ELEICAO"] == pl.Int32
    assert SCHEMA_SILVER["CD_MUNICIPIO"] == pl.Int32
    assert SCHEMA_SILVER["QT_APTOS"] == pl.Int64
    assert SCHEMA_SILVER["QT_COMPARECIMENTO"] == pl.Int64
    assert SCHEMA_SILVER["QT_ABSTENCAO"] == pl.Int64

    # Campos texto
    assert SCHEMA_SILVER["NM_MUNICIPIO"] == pl.Utf8
    assert SCHEMA_SILVER["SG_UF"] == pl.Utf8
    assert SCHEMA_SILVER["NOME_REGIAO"] == pl.Utf8

    # Campos decimais (taxas)
    assert SCHEMA_SILVER["TAXA_COMPARECIMENTO_PCT"] == pl.Float64
    assert SCHEMA_SILVER["TAXA_ABSTENCAO_PCT"] == pl.Float64

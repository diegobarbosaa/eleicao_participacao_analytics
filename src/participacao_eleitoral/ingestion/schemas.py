# participacao_eleitoral/ingestion/schemas.py

import polars as pl

SCHEMA_COMPARECIMENTO = {
    "DT_GERACAO": pl.Utf8,
    "HH_GERACAO": pl.Utf8,
    "ANO_ELEICAO": pl.Int32,
    "CD_TIPO_ELEICAO": pl.Int32,
    "NM_TIPO_ELEICAO": pl.Utf8,
    "NR_TURNO": pl.Int8,
    "CD_ELEICAO": pl.Int32,
    "DS_ELEICAO": pl.Utf8,
    "DT_ELEICAO": pl.Utf8,
    "TP_ABRANGENCIA": pl.Utf8,
    "SG_UF": pl.Utf8,
    "NM_UF": pl.Utf8,
    "CD_MUNICIPIO": pl.Int32,
    "NM_MUNICIPIO": pl.Utf8,
    "NR_ZONA": pl.Int32,
    "QT_APTOS": pl.Int64,
    "QT_COMPARECIMENTO": pl.Int64,
    "QT_ABSTENCOES": pl.Int64,
}


from participacao_eleitoral.ingestion.converter import CSVToParquetConverter
from participacao_eleitoral.ingestion.schemas.comparecimento import (
    SCHEMA_COMPARECIMENTO,
)


def test_converter_gera_parquet(tmp_path, logger):
    """
    Converter deve gerar Parquet válido.
    """

    csv = tmp_path / "input.csv"
    parquet = tmp_path / "output.parquet"

    csv.write_text(
        "ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCOES\n"
        "2022;12345;Recife;PE;1000;800;200\n"
    )

    converter = CSVToParquetConverter(logger=logger)

    result = converter.convert(
        csv_path=csv,
        parquet_path=parquet,
        schema=SCHEMA_COMPARECIMENTO,
        source="test",
    )

    assert parquet.exists()
    assert result.linhas == 1

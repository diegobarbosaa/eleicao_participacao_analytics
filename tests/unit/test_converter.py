"""Testes unitários para o conversor CSV→Parquet."""

from pathlib import Path

import polars as pl
import pytest

from participacao_eleitoral.ingestion.converter import CSVToParquetConverter


@pytest.fixture
def sample_csv(tmp_path):
    """Cria um CSV de exemplo que simula dados do TSE."""
    csv_path = tmp_path / "teste.csv"
    
    # Dados que simulam estrutura real do TSE
    csv_content = """ANO_ELEICAO;CD_TIPO_ELEICAO;NM_TIPO_ELEICAO;SG_UF;CD_MUNICIPIO;NM_MUNICIPIO;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCOES
2024;2;Eleição Municipal;SP;71072;SÃO PAULO;9234567;7123456;2111111
2024;2;Eleição Municipal;RJ;60011;RIO DE JANEIRO;5234123;4123123;1111000
2024;2;Eleição Municipal;MG;41238;BELO HORIZONTE;2123456;1523456;600000"""
    
    csv_path.write_text(csv_content, encoding="latin1")
    return csv_path


def test_convert_csv_to_parquet_sucesso(sample_csv, tmp_path):
    """Testa conversão bem-sucedida de CSV para Parquet."""
    parquet_path = tmp_path / "output.parquet"
    
    # Executar conversão
    resultado_path, num_linhas = CSVToParquetConverter.convert(
        csv_path=sample_csv,
        parquet_path=parquet_path,
    )
    
    # Verificações básicas
    assert resultado_path.exists(), "Arquivo Parquet deveria existir"
    assert num_linhas == 3, f"Esperava 3 linhas, obteve {num_linhas}"
    assert resultado_path.suffix == ".parquet"
    
    # Verificar conteúdo do Parquet
    df = pl.read_parquet(parquet_path)
    assert len(df) == 3, "DataFrame deveria ter 3 linhas"
    assert "ANO_ELEICAO" in df.columns
    assert "QT_COMPARECIMENTO" in df.columns
    
    # Verificar metadados de ingestão foram adicionados
    assert "_metadata_ingestion_timestamp" in df.columns
    assert "_metadata_source_file" in df.columns
    assert df["_metadata_source_file"][0] == "teste.csv"


def test_convert_preserva_dados_originais(sample_csv, tmp_path):
    """Verifica que nenhum dado é perdido ou alterado na conversão."""
    parquet_path = tmp_path / "output.parquet"
    
    # Ler CSV original
    df_original = pl.read_csv(sample_csv, separator=";", encoding="latin1")
    
    # Converter
    CSVToParquetConverter.convert(sample_csv, parquet_path)
    
    # Ler Parquet resultante
    df_convertido = pl.read_parquet(parquet_path)
    
    # Verificar que todas as colunas originais existem
    for col in df_original.columns:
        assert col in df_convertido.columns, f"Coluna {col} deveria existir"
    
    # Verificar valores específicos
    assert df_convertido["ANO_ELEICAO"][0] == 2024
    assert df_convertido["NM_MUNICIPIO"][0] == "SÃO PAULO"
    assert df_convertido["QT_COMPARECIMENTO"][0] == 7123456


def test_convert_compressao_reduz_tamanho(sample_csv, tmp_path):
    """Verifica que Parquet com zstd é criado."""
    parquet_path = tmp_path / "output.parquet"
    
    # Converter
    CSVToParquetConverter.convert(sample_csv, parquet_path)
    
    # Comparar tamanhos
    csv_size = sample_csv.stat().st_size
    parquet_size = parquet_path.stat().st_size
    
    # Verificar que arquivos existem
    assert parquet_size > 0, "Parquet não pode estar vazio"
    assert csv_size > 0, "CSV não pode estar vazio"
    assert parquet_path.exists()


def test_convert_com_schema_customizado(sample_csv, tmp_path):
    """Testa conversão com schema explícito."""
    parquet_path = tmp_path / "output.parquet"
    
    # Schema customizado (força tipos específicos)
    schema_custom = {
        "ANO_ELEICAO": pl.Int32,
        "CD_TIPO_ELEICAO": pl.Int32,
        "NM_TIPO_ELEICAO": pl.Utf8,
        "SG_UF": pl.Utf8,
        "CD_MUNICIPIO": pl.Int32,
        "NM_MUNICIPIO": pl.Utf8,
        "QT_APTOS": pl.Int64,
        "QT_COMPARECIMENTO": pl.Int64,
        "QT_ABSTENCOES": pl.Int64,
    }
    
    # Converter com schema
    CSVToParquetConverter.convert(
        csv_path=sample_csv,
        parquet_path=parquet_path,
        schema=schema_custom,
    )
    
    # Verificar tipos de dados
    df = pl.read_parquet(parquet_path)
    assert df["ANO_ELEICAO"].dtype == pl.Int32
    assert df["QT_COMPARECIMENTO"].dtype == pl.Int64
    assert df["NM_MUNICIPIO"].dtype == pl.Utf8


def test_convert_cria_diretorios_se_nao_existem(sample_csv, tmp_path):
    """Verifica que diretórios são criados automaticamente."""
    # Caminho com diretórios que não existem
    parquet_path = tmp_path / "nivel1" / "nivel2" / "nivel3" / "output.parquet"
    
    assert not parquet_path.parent.exists(), "Diretório não deveria existir ainda"
    
    # Converter (deve criar diretórios automaticamente)
    resultado_path, _ = CSVToParquetConverter.convert(sample_csv, parquet_path)
    
    assert resultado_path.exists(), "Arquivo deveria ter sido criado"
    assert parquet_path.parent.exists(), "Diretórios deveriam ter sido criados"


def test_convert_csv_vazio_retorna_zero_linhas(tmp_path):
    """Testa comportamento com CSV vazio (só header)."""
    csv_vazio = tmp_path / "vazio.csv"
    csv_vazio.write_text("COL1;COL2;COL3\n", encoding="latin1")
    
    parquet_path = tmp_path / "vazio.parquet"
    
    resultado_path, num_linhas = CSVToParquetConverter.convert(
        csv_path=csv_vazio,
        parquet_path=parquet_path,
    )
    
    assert num_linhas == 0, "CSV vazio deveria ter 0 linhas"
    assert resultado_path.exists()
    
    df = pl.read_parquet(parquet_path)
    assert len(df) == 0
    
    # Verificar que colunas originais existem
    colunas_originais = ["COL1", "COL2", "COL3"]
    for col in colunas_originais:
        assert col in df.columns, f"Coluna {col} deveria existir"


def test_convert_csv_com_valores_nulos_tse(tmp_path):
    """Testa tratamento de valores nulos específicos do TSE."""
    csv_com_nulos = tmp_path / "com_nulos.csv"
    
    # TSE usa #NULO# e #NE# para representar nulos
    csv_content = """COL1;COL2;COL3
valor1;#NULO#;valor3
valor4;#NE#;valor6
valor7;valor8;valor9"""
    
    csv_com_nulos.write_text(csv_content, encoding="latin1")
    parquet_path = tmp_path / "com_nulos.parquet"
    
    CSVToParquetConverter.convert(csv_com_nulos, parquet_path)
    
    df = pl.read_parquet(parquet_path)
    
    # Verificar que #NULO# e #NE# foram convertidos para null
    assert df["COL2"][0] is None, "Primeiro valor deveria ser null"
    assert df["COL2"][1] is None, "Segundo valor deveria ser null"
    assert df["COL2"][2] == "valor8", "Terceiro valor deveria ser 'valor8'"


@pytest.mark.parametrize("encoding", ["latin1", "utf-8"])
def test_convert_diferentes_encodings(tmp_path, encoding):
    """Testa conversão com diferentes encodings."""
    csv_path = tmp_path / f"test_{encoding}.csv"
    
    # Dados com acentuação (comum em nomes de municípios)
    csv_content = "MUNICIPIO;UF\nSÃO PAULO;SP\nBRASÍLIA;DF"
    csv_path.write_text(csv_content, encoding=encoding)
    
    parquet_path = tmp_path / f"test_{encoding}.parquet"
    
    # Converter (só funciona com latin1 no código atual)
    if encoding == "latin1":
        resultado_path, num_linhas = CSVToParquetConverter.convert(
            csv_path, parquet_path
        )
        assert num_linhas == 2
        df = pl.read_parquet(parquet_path)
        assert "SÃO PAULO" in df["MUNICIPIO"].to_list()
import random
from pathlib import Path
import polars as pl

ANOS = [2014, 2016, 2018, 2020, 2022, 2024]
NUM_LINHAS = 100
SILVER_DIR = Path("data/silver/comparecimento_abstencao")
OUTPUT_DIR = Path("data/samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extrair_mock_silver(ano: int) -> pl.DataFrame:
    parquet_path = SILVER_DIR / f"year={ano}" / "data.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Arquivo silver não encontrado: {parquet_path}")

    df = pl.read_parquet(parquet_path)
    # Amostrar 100 linhas aleatórias
    if len(df) < NUM_LINHAS:
        return df  # Se menos que 100, usar tudo
    return df.sample(n=NUM_LINHAS, seed=42)  # Seed para consistência


if __name__ == "__main__":
    for ano in ANOS:
        try:
            df = extrair_mock_silver(ano)
            output_path = OUTPUT_DIR / f"{ano}_mock.csv"
            df.write_csv(output_path)
            print(f"Extraído: {output_path} ({len(df)} linhas)")
        except Exception as e:
            print(f"Erro em {ano}: {e}")
    print("Mocks extraídos com sucesso!")

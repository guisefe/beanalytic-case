import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.quality import check_not_empty, check_no_nulls, check_column_types, check_value_range

INPUT_PATH = Path("data/bronze/selic_raw.parquet")
OUTPUT_PATH = Path("data/silver/selic_clean.parquet")


def load_bronze() -> pd.DataFrame:
    """Carrega os dados brutos da camada Bronze."""
    df = pd.read_parquet(INPUT_PATH)
    print(f"[{datetime.now():%H:%M:%S}] {len(df)} registros carregados do Bronze.")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpeza e padronização dos dados.
    Aqui tomamos decisões explícitas sobre tipos e nulos —
    nada é assumido silenciosamente.
    """

    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    nulos = df.isnull().sum()
    if nulos.any():
        print(f"[AVISO] Nulos encontrados:\n{nulos[nulos > 0]}")

    antes = len(df)
    df = df.dropna(subset=["data", "valor"])
    depois = len(df)

    if antes != depois:
        print(f"[{datetime.now():%H:%M:%S}] {antes - depois} registros removidos por nulos.")

    print(f"[{datetime.now():%H:%M:%S}] Transformação concluída. {len(df)} registros válidos.")
    return df


def save_silver(df: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)
    print(f"[{datetime.now():%H:%M:%S}] Salvo em: {OUTPUT_PATH}")


def run():
    df = load_bronze()
    df = transform(df)

    # Checagens de qualidade — Silver
    check_not_empty(df, layer="Silver")
    check_no_nulls(df, columns=["data", "valor"], layer="Silver")
    check_column_types(df, {"valor": "float", "ano": "int", "mes": "int"}, layer="Silver")
    check_value_range(df, column="valor", min_val=0.0, max_val=5.0, layer="Silver")

    save_silver(df)


if __name__ == "__main__":
    run()

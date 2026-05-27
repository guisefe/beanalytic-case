import pandas as pd
from pathlib import Path
from datetime import datetime

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

    # Converte data de string BR para datetime
    # errors='coerce' transforma datas inválidas em NaT em vez de explodir
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")

    # Garante que valor é float — defensivo caso a API mude comportamento
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Adiciona colunas de contexto — úteis na Gold sem precisar recalcular
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    # Checagem de qualidade — loga mas não explode
    nulos = df.isnull().sum()
    if nulos.any():
        print(f"[AVISO] Nulos encontrados:\n{nulos[nulos > 0]}")

    # Remove linhas com data ou valor nulo — sem esses dois, o registro é inútil
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
    save_silver(df)


if __name__ == "__main__":
    run()

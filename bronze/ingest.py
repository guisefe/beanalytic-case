import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

BCB_URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
    "?formato=json&dataInicial=01/01/2020&dataFinal=31/12/2024"
)

OUTPUT_PATH = Path("data/bronze/selic_raw.parquet")


def fetch_selic() -> pd.DataFrame:
    """
    Consome a API do BCB e retorna os dados brutos.
    Nada é convertido aqui — tudo chega como string, tudo sai como string.
    Limpeza é responsabilidade da camada Silver.
    """
    print(f"[{datetime.now():%H:%M:%S}] Conectando na API do BCB...")

    response = requests.get(BCB_URL, timeout=30)
    response.raise_for_status()  # se vier erro 4xx/5xx, estoura aqui mesmo

    raw = response.json()

    if not raw:
        raise ValueError("API retornou lista vazia — verifique o intervalo de datas.")

    df = pd.DataFrame(raw)
    print(f"[{datetime.now():%H:%M:%S}] {len(df)} registros recebidos.")

    return df


def save_bronze(df: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)
    print(f"[{datetime.now():%H:%M:%S}] Salvo em: {OUTPUT_PATH}")


def run():
    df = fetch_selic()
    save_bronze(df)


if __name__ == "__main__":
    run()

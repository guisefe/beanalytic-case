import sys
import logging
from pathlib import Path

import requests
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BCB_URL, BRONZE_PATH
from utils.quality import check_not_empty, check_no_nulls

log = logging.getLogger(__name__)


def fetch_selic() -> pd.DataFrame:
    # sem auth, mas a API do BCB é lenta às vezes — timeout generoso
    log.info("buscando dados da SELIC...")
    response = requests.get(BCB_URL, timeout=30)
    response.raise_for_status()

    raw = response.json()
    if not raw:
        raise ValueError("API retornou vazia — confere o intervalo de datas")

    df = pd.DataFrame(raw)
    log.info(f"{len(df)} registros recebidos")
    return df


def save_bronze(df: pd.DataFrame) -> None:
    BRONZE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(BRONZE_PATH, index=False)
    log.info(f"bronze salvo em {BRONZE_PATH}")


def run():
    df = fetch_selic()
    check_not_empty(df, layer="Bronze")
    check_no_nulls(df, columns=["data", "valor"], layer="Bronze")
    save_bronze(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()

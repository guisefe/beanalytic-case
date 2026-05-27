import sys
import logging
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SILVER_PATH, BRONZE_PATH
from utils.quality import check_not_empty, check_no_nulls, check_column_types, check_value_range

log = logging.getLogger(__name__)


def load_bronze() -> pd.DataFrame:
    df = pd.read_parquet(BRONZE_PATH)
    log.info(f"{len(df)} registros carregados do Bronze")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # data vem como string BR — converte pra datetime padrão
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    antes = len(df)
    df = df.dropna(subset=["data", "valor"])

    if antes != len(df):
        log.warning(f"{antes - len(df)} registros removidos por nulos")

    log.info(f"{len(df)} registros válidos após transformação")
    return df


def save_silver(df: pd.DataFrame) -> None:
    SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER_PATH, index=False)
    log.info(f"silver salvo em {SILVER_PATH}")


def run():
    df = load_bronze()
    df = transform(df)
    check_not_empty(df, layer="Silver")
    check_no_nulls(df, columns=["data", "valor"], layer="Silver")
    check_column_types(df, {"valor": "float", "ano": "int", "mes": "int"}, layer="Silver")
    check_value_range(df, column="valor", min_val=0.0, max_val=5.0, layer="Silver")
    save_silver(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()

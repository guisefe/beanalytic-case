import sys
import logging
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SILVER_PATH, GOLD_PATH
from utils.quality import check_not_empty, check_no_nulls, check_column_types

log = logging.getLogger(__name__)


def load_silver() -> pd.DataFrame:
    df = pd.read_parquet(SILVER_PATH)
    log.info(f"{len(df)} registros carregados do Silver")
    return df


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["ano", "mes"])
        .agg(
            media_mensal=("valor", "mean"),
            min_diario=("valor", "min"),
            max_diario=("valor", "max"),
            dias_uteis=("valor", "count"),
        )
        .reset_index()
    )

    # variação percentual mês a mês — NaN no primeiro mês é esperado
    monthly["variacao_mensal"] = monthly["media_mensal"].pct_change() * 100

    # acumulado anual via juros compostos — (1 + taxa_diaria).prod() - 1
    annual = (
        df.groupby("ano")["valor"]
        .apply(lambda x: ((1 + x / 100).prod() - 1) * 100)
        .reset_index()
        .rename(columns={"valor": "acumulado_anual"})
    )

    result = monthly.merge(annual, on="ano", how="left")
    log.info(f"{len(result)} meses agregados")
    return result


def save_gold(df: pd.DataFrame) -> None:
    GOLD_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(GOLD_PATH, index=False)

    csv_path = GOLD_PATH.with_suffix(".csv")
    df.to_csv(csv_path, index=False)

    log.info(f"gold salvo em {GOLD_PATH}")
    log.info(f"csv salvo em {csv_path}")

    log.info("Preview da camada Gold:")
    log.info(f"\n{df.head().to_string()}")

def run():
    df = load_silver()
    df = aggregate(df)
    check_not_empty(df, layer="Gold")
    check_no_nulls(df, columns=["ano", "mes", "media_mensal"], layer="Gold")
    check_column_types(df, {"media_mensal": "float", "dias_uteis": "int"}, layer="Gold")
    save_gold(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()

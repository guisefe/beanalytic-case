import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.quality import check_not_empty, check_no_nulls, check_column_types

INPUT_PATH = Path("data/silver/selic_clean.parquet")
OUTPUT_PATH = Path("data/gold/selic_metrics.parquet")


def load_silver() -> pd.DataFrame:
    """Carrega os dados limpos da camada Silver."""
    df = pd.read_parquet(INPUT_PATH)
    print(f"[{datetime.now():%H:%M:%S}] {len(df)} registros carregados do Silver.")
    return df


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera métricas consolidadas por mês.
    Todas as decisões de agregação são explícitas e justificadas.
    """
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

    monthly["variacao_mensal"] = monthly["media_mensal"].pct_change() * 100

    annual = (
        df.groupby("ano")["valor"]
        .apply(lambda x: ((1 + x / 100).prod() - 1) * 100)
        .reset_index()
        .rename(columns={"valor": "acumulado_anual"})
    )

    result = monthly.merge(annual, on="ano", how="left")

    print(f"[{datetime.now():%H:%M:%S}] {len(result)} meses agregados.")
    return result


def save_gold(df: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)
    print(f"[{datetime.now():%H:%M:%S}] Salvo em: {OUTPUT_PATH}")


def run():
    df = load_silver()
    df = aggregate(df)

    # Checagens de qualidade — Gold
    check_not_empty(df, layer="Gold")
    check_no_nulls(df, columns=["ano", "mes", "media_mensal"], layer="Gold")
    check_column_types(df, {"media_mensal": "float", "dias_uteis": "int"}, layer="Gold")

    save_gold(df)


if __name__ == "__main__":
    run()

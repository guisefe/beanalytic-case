import pandas as pd
from pathlib import Path
from datetime import datetime

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

    # Agrupa por ano e mês — cada linha do resultado = um mês
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

    # Variação mensal — quanto a média mudou em relação ao mês anterior
    # pct_change() calcula a variação percentual entre linhas consecutivas
    monthly["variacao_mensal"] = monthly["media_mensal"].pct_change() * 100

    # Taxa acumulada anual — produto dos fatores diários agrupado por ano
    # (1 + taxa_diaria) composto ao longo dos dias úteis do ano
    annual = (
        df.groupby("ano")["valor"]
        .apply(lambda x: ((1 + x / 100).prod() - 1) * 100)
        .reset_index()
        .rename(columns={"valor": "acumulado_anual"})
    )

    # Junta as métricas mensais com o acumulado anual
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
    save_gold(df)


if __name__ == "__main__":
    run()

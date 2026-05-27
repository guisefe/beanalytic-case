import logging

import pandas as pd

log = logging.getLogger(__name__)


def check_not_empty(df: pd.DataFrame, layer: str) -> None:
    if df.empty:
        raise ValueError(f"[{layer}] DataFrame vazio — pipeline abortado.")
    log.info(f"[{layer}] OK — {len(df)} registros")


def check_no_nulls(df: pd.DataFrame, columns: list, layer: str) -> None:
    for col in columns:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            raise ValueError(
                f"[{layer}] coluna '{col}' tem {nulls} nulos — pipeline abortado."
            )
    log.info(f"[{layer}] OK — sem nulos em {columns}")


def check_column_types(df: pd.DataFrame, expected: dict, layer: str) -> None:
    for col, expected_type in expected.items():
        actual = str(df[col].dtype)
        if expected_type not in actual:
            raise ValueError(
                f"[{layer}] '{col}' deveria ser '{expected_type}' mas é '{actual}'"
            )
    log.info(f"[{layer}] OK — tipos corretos em {list(expected.keys())}")


def check_value_range(df: pd.DataFrame, column: str, min_val: float, max_val: float, layer: str) -> None:
    out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
    if not out_of_range.empty:
        raise ValueError(
            f"[{layer}] {len(out_of_range)} valores fora do range [{min_val}, {max_val}] em '{column}'"
        )
    log.info(f"[{layer}] OK — '{column}' dentro do range esperado")

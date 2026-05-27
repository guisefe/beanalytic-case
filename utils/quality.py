import pandas as pd
from datetime import datetime


def check_not_empty(df: pd.DataFrame, layer: str) -> None:
    """Garante que o DataFrame não está vazio."""
    if df.empty:
        raise ValueError(f"[{layer}] DataFrame vazio — pipeline abortado.")
    print(f"[{datetime.now():%H:%M:%S}] [{layer}] OK — {len(df)} registros.")


def check_no_nulls(df: pd.DataFrame, columns: list, layer: str) -> None:
    """Garante que colunas críticas não têm nulos."""
    for col in columns:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            raise ValueError(
                f"[{layer}] Coluna '{col}' tem {nulls} valores nulos — pipeline abortado."
            )
    print(f"[{datetime.now():%H:%M:%S}] [{layer}] OK — sem nulos em {columns}.")


def check_column_types(df: pd.DataFrame, expected: dict, layer: str) -> None:
    """
    Verifica se as colunas têm os tipos esperados.
    expected = {"coluna": "tipo_esperado"}
    """
    for col, expected_type in expected.items():
        actual = str(df[col].dtype)
        if expected_type not in actual:
            raise ValueError(
                f"[{layer}] Coluna '{col}' deveria ser '{expected_type}' mas é '{actual}'."
            )
    print(f"[{datetime.now():%H:%M:%S}] [{layer}] OK — tipos corretos em {list(expected.keys())}.")


def check_value_range(df: pd.DataFrame, column: str, min_val: float, max_val: float, layer: str) -> None:
    """Garante que os valores estão dentro de um range esperado."""
    out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
    if not out_of_range.empty:
        raise ValueError(
            f"[{layer}] {len(out_of_range)} valores fora do range [{min_val}, {max_val}] em '{column}'."
        )
    print(f"[{datetime.now():%H:%M:%S}] [{layer}] OK — valores de '{column}' dentro do range esperado.")

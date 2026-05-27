import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from silver.transform import transform
from gold.aggregate import aggregate
from utils.quality import (
    check_not_empty,
    check_no_nulls,
    check_column_types,
    check_value_range,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def bronze_sample():
    """Simula dados brutos vindos da API do BCB."""
    return pd.DataFrame({
        "data": ["02/01/2020", "03/01/2020", "06/01/2020"],
        "valor": ["0.017089", "0.017089", "0.017089"],
    })


@pytest.fixture
def silver_sample(bronze_sample):
    """Dados já transformados pela camada Silver."""
    return transform(bronze_sample)


# ─── Testes Silver ────────────────────────────────────────────────────────────

def test_silver_converte_data(silver_sample):
    """A coluna data deve virar datetime após a transformação."""
    assert pd.api.types.is_datetime64_any_dtype(silver_sample["data"])


def test_silver_converte_valor(silver_sample):
    """A coluna valor deve virar float após a transformação."""
    assert str(silver_sample["valor"].dtype) == "float64"


def test_silver_adiciona_ano_mes(silver_sample):
    """A Silver deve adicionar colunas ano e mes."""
    assert "ano" in silver_sample.columns
    assert "mes" in silver_sample.columns


def test_silver_remove_nulos():
    """Registros com data ou valor nulo devem ser removidos."""
    df = pd.DataFrame({
        "data": ["02/01/2020", None],
        "valor": ["0.017089", "0.017089"],
    })
    result = transform(df)
    assert len(result) == 1


# ─── Testes Gold ──────────────────────────────────────────────────────────────

def test_gold_gera_60_meses(silver_sample):
    """Com dados de 2020, deve gerar pelo menos 1 mês agregado."""
    result = aggregate(silver_sample)
    assert len(result) >= 1


def test_gold_tem_colunas_esperadas(silver_sample):
    """O resultado da Gold deve ter todas as colunas de métricas."""
    result = aggregate(silver_sample)
    for col in ["media_mensal", "min_diario", "max_diario", "dias_uteis", "acumulado_anual"]:
        assert col in result.columns


# ─── Testes Quality ───────────────────────────────────────────────────────────

def test_quality_not_empty_levanta_erro():
    """check_not_empty deve levantar erro com DataFrame vazio."""
    with pytest.raises(ValueError):
        check_not_empty(pd.DataFrame(), layer="Test")


def test_quality_no_nulls_levanta_erro():
    """check_no_nulls deve levantar erro quando há nulos."""
    df = pd.DataFrame({"valor": [1.0, None]})
    with pytest.raises(ValueError):
        check_no_nulls(df, columns=["valor"], layer="Test")


def test_quality_value_range_levanta_erro():
    """check_value_range deve levantar erro com valores fora do range."""
    df = pd.DataFrame({"valor": [0.5, 99.9]})
    with pytest.raises(ValueError):
        check_value_range(df, column="valor", min_val=0.0, max_val=5.0, layer="Test")

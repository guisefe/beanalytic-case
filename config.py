import os
from pathlib import Path

# Raiz do projeto
PROJECT_ROOT = Path(__file__).parent

# URL da API do Banco Central
BCB_URL = os.getenv(
    "BCB_URL",
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
    "?formato=json&dataInicial=01/01/2020&dataFinal=31/12/2024"
)

# Paths das camadas
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze" / "selic_raw.parquet"
SILVER_PATH = PROJECT_ROOT / "data" / "silver" / "selic_clean.parquet"
GOLD_PATH   = PROJECT_ROOT / "data" / "gold"   / "selic_metrics.parquet"

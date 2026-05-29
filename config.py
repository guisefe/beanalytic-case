import os
from pathlib import Path

# Raiz do projeto
PROJECT_ROOT = Path(__file__).parent

# Datas configuráveis via variável de ambiente
DATA_INICIAL = os.getenv("DATA_INICIAL", "01/01/2020")
DATA_FINAL   = os.getenv("DATA_FINAL",   "31/12/2024")

# URL da API do Banco Central
BCB_URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
    f"?formato=json&dataInicial={DATA_INICIAL}&dataFinal={DATA_FINAL}"
)

# Paths das camadas
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze" / "selic_raw.parquet"
SILVER_PATH = PROJECT_ROOT / "data" / "silver" / "selic_clean.parquet"
GOLD_PATH   = PROJECT_ROOT / "data" / "gold"   / "selic_metrics.parquet"

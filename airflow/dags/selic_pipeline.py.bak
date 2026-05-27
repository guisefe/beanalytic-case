import sys
from pathlib import Path
from datetime import datetime, timedelta

from airflow.sdk import dag, task

# Aponta para a raiz do projeto — onde vivem bronze/, silver/ e gold/
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from bronze.ingest import run as bronze_run
from silver.transform import run as silver_run
from gold.aggregate import run as gold_run


default_args = {
    "owner": "guilherme.senis",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


@dag(
    dag_id="selic_pipeline",
    description="Pipeline Medallion da Taxa SELIC — BCB API → Bronze → Silver → Gold",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["bcb", "selic", "medallion"],
)
def selic_pipeline():

    @task()
    def ingestao_bronze():
        """Task 1 — Consome a API do BCB e salva dados brutos em Parquet."""
        bronze_run()

    @task()
    def transformacao_silver():
        """Task 2 — Limpa e padroniza os dados do Bronze."""
        silver_run()

    @task()
    def agregacao_gold():
        """Task 3 — Gera métricas mensais e acumulado anual."""
        gold_run()

    ingestao_bronze() >> transformacao_silver() >> agregacao_gold()


selic_pipeline()

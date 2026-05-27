import sys
from pathlib import Path
from datetime import datetime, timedelta

from airflow.sdk import dag, task

# Garante que os módulos bronze/silver/gold são encontrados
sys.path.insert(0, str(Path(__file__).parent.parent))

from bronze.ingest import run as bronze_run
from silver.transform import run as silver_run
from gold.aggregate import run as gold_run


default_args = {
    "owner": "guilherme.senis",
    "retries": 3,                          # tenta 3x antes de desistir
    "retry_delay": timedelta(minutes=5),   # espera 5min entre tentativas
    "email_on_failure": False,
}


@dag(
    dag_id="selic_pipeline",
    description="Pipeline Medallion da Taxa SELIC — BCB API → Bronze → Silver → Gold",
    schedule=None,          # roda sob demanda; fácil de mudar pra @daily depois
    start_date=datetime(2024, 1, 1),
    catchup=False,          # não tenta recuperar execuções passadas
    default_args=default_args,
    tags=["bcb", "selic", "medallion"],
)
def selic_pipeline():

    @task()
    def ingestao_bronze():
        """
        Task 1 — Bronze
        Consome a API do BCB e salva os dados brutos em Parquet.
        Nenhuma transformação aqui — o dado chega como veio.
        """
        bronze_run()

    @task()
    def transformacao_silver():
        """
        Task 2 — Silver
        Limpa e padroniza os dados do Bronze:
        converte tipos, trata nulos e padroniza datas.
        """
        silver_run()

    @task()
    def agregacao_gold():
        """
        Task 3 — Gold
        Gera métricas consolidadas: média mensal,
        variação mensal e taxa acumulada anual.
        """
        gold_run()

    # Define a ordem de execução — Bronze → Silver → Gold
    ingestao_bronze() >> transformacao_silver() >> agregacao_gold()


selic_pipeline()

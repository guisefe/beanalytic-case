# beAnalytic Case — Pipeline SELIC

Pipeline de dados construído com Apache Airflow seguindo a arquitetura Medallion (Bronze → Silver → Gold), consumindo dados reais da API do Banco Central do Brasil.

## Arquitetura

Cada camada é isolada: se a Silver falhar, o Bronze original permanece intacto para reprocessamento.

- **Bronze** → dados brutos em Parquet, sem transformações
- **Silver** → limpeza de tipos, conversão de datas, tratamento de nulos
- **Gold** → média mensal, variação mensal, taxa acumulada anual

## Estrutura do Projeto

- dags/selic_pipeline.py — DAG principal do Airflow
- bronze/ingest.py — Ingestão da API do BCB
- silver/transform.py — Limpeza e padronização
- gold/aggregate.py — Métricas consolidadas

## Decisões Técnicas

**Por que Parquet?** Formato colunar, comprimido e com tipagem — padrão da indústria. CSV seria mais lento e sem controle de tipos.

**Por que schedule=None?** O pipeline consome dados históricos (2020–2024). Faz mais sentido rodar sob demanda do que agendar diariamente dados que não mudam.

**Por que Bronze/Silver/Gold?** Rastreabilidade. Se a lógica de agregação mudar, reprocessamos só a Gold sem tocar nos dados brutos.

**Tratamento de erros:** retries=3 com delay de 5 minutos. A API do BCB tem latência variável — essa configuração absorve falhas transitórias sem intervenção manual.

## Como Executar Localmente

Pré-requisitos: Python 3.12+ e pip.

    git clone https://github.com/guisefe/beanalytic-case
    cd beanalytic-case
    pip install -r requirements.txt
    export AIRFLOW_HOME=$(pwd)/airflow
    airflow db migrate
    airflow standalone

Depois acesse http://localhost:8080 e acione a DAG selic_pipeline manualmente.

## Resultado

| Camada | Registros |
|--------|-----------|
| Bronze | 1.255 dias brutos |
| Silver | 1.255 dias limpos |
| Gold   | 60 meses agregados |

## Stack

- Apache Airflow 3.x
- Python 3.12
- Pandas + PyArrow
- API pública do Banco Central do Brasil
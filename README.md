[![Pipeline Tests](https://github.com/guisefe/beanalytic-case/actions/workflows/test.yml/badge.svg)](https://github.com/guisefe/beanalytic-case/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Airflow](https://img.shields.io/badge/Airflow-3.x-red)
![Parquet](https://img.shields.io/badge/Format-Parquet-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

# Pipeline SELIC — beAnalytic Case

Pipeline de dados construído com Apache Airflow e arquitetura Medallion, consumindo dados reais da taxa SELIC via API do Banco Central do Brasil.

O objetivo é demonstrar como estruturar um pipeline modular, testado e pronto para produção — da ingestão bruta até métricas consolidadas prontas para análise.

## Arquitetura

Cada camada tem responsabilidade única e é isolada das demais. Se a Silver falhar, o dado original no Bronze permanece intacto para reprocessamento.

- **Bronze** — dado bruto exatamente como veio da API, sem nenhuma transformação
- **Silver** — limpeza de tipos, conversão de datas, remoção de nulos
- **Gold** — média mensal, variação mês a mês e taxa acumulada anual

## Estrutura

- dags/selic_pipeline.py — DAG principal, orquestra as 3 tasks
- bronze/ingest.py — consome a API do BCB
- silver/transform.py — limpa e padroniza os dados
- gold/aggregate.py — gera as métricas consolidadas
- utils/quality.py — checagens de qualidade entre camadas
- config.py — paths e variáveis centralizados
- tests/test_pipeline.py — testes unitários (9/9)

## Decisões Técnicas

**Parquet em vez de CSV** — formato colunar e comprimido, com tipagem nativa. Padrão da indústria para pipelines analíticos.

**schedule=None** — os dados são históricos (2020-2024) e não mudam. Rodar sob demanda faz mais sentido do que agendar execuções diárias desnecessárias.

**Camadas separadas** — rastreabilidade. Se a lógica de agregação mudar, reprocessamos só a Gold sem tocar nos dados brutos.

**retries=3 com delay de 5 minutos** — a API do BCB tem latência variável. Essa configuração absorve falhas transitórias sem intervenção manual.

**Checagens de qualidade** — cada camada valida volume, nulos, tipos e range de valores antes de passar os dados adiante. Falha cedo, falha rápido.

**Dockerfile customizado** — a imagem oficial do Airflow no Docker Hub é 2.x, incompatível com a API 3.x usada no projeto. A imagem customizada garante paridade entre desenvolvimento e produção.

## Como Executar com Docker (recomendado)

Pré-requisitos: Docker e Docker Compose instalados.

    git clone https://github.com/guisefe/beanalytic-case
    cd beanalytic-case
    docker compose up --build

Na primeira execução o build pode levar 5-10 minutos — o Airflow é instalado com as constraints oficiais para garantir compatibilidade total.

Aguarda o container estabilizar e acessa http://localhost:8080
Login: admin / Senha: admin

Aciona a DAG selic_pipeline manualmente pelo painel.

O ambiente foi desenvolvido via GitHub Codespaces, garantindo reprodutibilidade independente do sistema operacional local.

## Como Executar sem Docker

Pré-requisitos: Python 3.12+ e pip.

    git clone https://github.com/guisefe/beanalytic-case
    cd beanalytic-case
    pip install -r requirements.txt
    export AIRFLOW_HOME=$(pwd)/airflow
    export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
    airflow db migrate
    airflow dags test selic_pipeline

## Testes

    pytest tests/ -v

| Teste | O que valida |
|-------|-------------|
| test_silver_converte_data | data vira datetime após transformação |
| test_silver_converte_valor | valor vira float após transformação |
| test_silver_adiciona_ano_mes | colunas ano e mes são criadas |
| test_silver_remove_nulos | registros com nulos são removidos |
| test_gold_gera_60_meses | Gold gera pelo menos 1 mês agregado |
| test_gold_tem_colunas_esperadas | Gold tem todas as colunas de métricas |
| test_quality_not_empty_levanta_erro | erro se DataFrame vazio |
| test_quality_no_nulls_levanta_erro | erro se há nulos em colunas críticas |
| test_quality_value_range_levanta_erro | erro se valores fora do range esperado |

## Resultado

| Camada | Registros |
|--------|-----------|
| Bronze | 1.255 dias brutos |
| Silver | 1.255 dias válidos |
| Gold | 60 meses agregados |

## Stack

- Apache Airflow 3.x
- Python 3.12
- Pandas + PyArrow + FastParquet
- Docker + Docker Compose
- pytest + GitHub Actions
- API pública do Banco Central do Brasil
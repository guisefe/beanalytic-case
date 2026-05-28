FROM python:3.12-slim

# dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# usuário airflow — boa prática de segurança
RUN useradd -ms /bin/bash airflow
USER airflow
WORKDIR /opt/airflow

# instala Airflow 3.x com PostgreSQL
RUN pip install --no-cache-dir --user \
    apache-airflow==3.2.1 \
    apache-airflow-providers-postgres \
    pandas==3.0.3 \
    requests==2.32.5 \
    pyarrow==24.0.0 \
    fastparquet==2026.5.0

ENV PATH="/home/airflow/.local/bin:$PATH"
ENV AIRFLOW_HOME=/opt/airflow

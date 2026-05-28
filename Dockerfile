FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash airflow \
    && mkdir -p /opt/airflow \
    && chown -R airflow:airflow /opt/airflow

USER airflow
WORKDIR /opt/airflow

ENV PATH="/home/airflow/.local/bin:$PATH"
ENV AIRFLOW_HOME=/opt/airflow

ARG AIRFLOW_VERSION=3.2.1
ARG PYTHON_VERSION=3.12
ARG CONSTRAINT_URL=https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt

RUN pip install --no-cache-dir --user \
    "apache-airflow[postgres]==${AIRFLOW_VERSION}" \
    --constraint "${CONSTRAINT_URL}"

RUN pip install --no-cache-dir --user \
    pandas==3.0.3 \
    requests==2.32.5 \
    pyarrow==24.0.0 \
    fastparquet==2026.5.0

FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY cli/ cli/
COPY dbt_project/ dbt_project/
COPY scripts/ scripts/

RUN pip install uv
RUN uv pip install --system -e .

RUN mkdir -p /app/data

ENV DBT_DB_PATH=/app/data/capstone.duckdb

CMD ["python", "-m", "cli.main", "--help"]

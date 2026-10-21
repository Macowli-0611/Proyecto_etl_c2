# Dockerfile for Second Delivery ETL Pipeline & Airflow Environment
FROM python:3.11-slim

WORKDIR /opt/airflow

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and configurations
COPY . .

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=/opt/airflow
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/run_pipeline.py"]

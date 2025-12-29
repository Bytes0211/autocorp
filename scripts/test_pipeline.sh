#!/bin/bash
# test_glue_pipeline.sh
set -e
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting AutoCorp ETL Pipeline Test..."
# Dimension tables
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running dimension table ETL jobs..."
CUSTOMERS_RUN=$(aws glue start-job-run --job-name autocorp-customers-etl-dev --query 'JobRunId' --output text)
PARTS_RUN=$(aws glue start-job-run --job-name autocorp-auto-parts-etl-dev --query 'JobRunId' --output text)
SERVICE_RUN=$(aws glue start-job-run --job-name autocorp-service-etl-dev --query 'JobRunId' --output text)
SERVICE_PARTS_RUN=$(aws glue start-job-run --job-name autocorp-service-parts-etl-dev --query 'JobRunId' --output text)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Waiting for dimension jobs to complete..."
sleep 300  # Wait 5 minutes
# Transactional tables
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running transactional table ETL jobs..."
SALES_ORDER_RUN=$(aws glue start-job-run --job-name autocorp-sales-order-etl-dev --query 'JobRunId' --output text)
ORDER_PARTS_RUN=$(aws glue start-job-run --job-name autocorp-sales-order-parts-etl-dev --query 'JobRunId' --output text)
ORDER_SERVICES_RUN=$(aws glue start-job-run --job-name autocorp-sales-order-services-etl-dev --query 'JobRunId' --output text)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Waiting for transactional jobs to complete..."
sleep 300  # Wait 5 minutes
# Analytics layer
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running analytics layer ETL jobs..."
aws glue start-job-run --job-name autocorp-analytics-sales-order-fact-dev
aws glue start-job-run --job-name autocorp-analytics-line-items-dev
aws glue start-job-run --job-name autocorp-analytics-service-parts-catalog-dev
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pipeline test initiated. Check CloudWatch dashboard for results."

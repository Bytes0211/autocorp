#!/bin/bash

# Check if query string is provided
if [ -z "$1" ]; then
  echo "Usage: $0 '<SQL_QUERY>' [DATABASE] [WORKGROUP] [S3_OUTPUT_LOCATION]"
  echo "Example: $0 'SELECT COUNT(*) FROM my_table' my_database my-workgroup s3://my-bucket/athena-results/"
  exit 1
fi

QUERY_STRING="$1"
DATABASE="${2:-my_database}"
WORKGROUP="${3:-my-workgroup}"
OUTPUT_LOCATION="${4:-s3://my-bucket/athena-results/}"

# Submit query
QUERY_ID=$(aws athena start-query-execution \
  --query-string "$QUERY_STRING" \
  --query-execution-context Database="$DATABASE" \
  --work-group "$WORKGROUP" \
  --result-configuration OutputLocation="$OUTPUT_LOCATION" \
  --query QueryExecutionId \
  --output text)

echo "Query ID: $QUERY_ID"

# Wait for completion
while true; do
  STATUS=$(aws athena get-query-execution --query-execution-id $QUERY_ID \
    --query 'QueryExecution.Status.State' --output text)
  if [[ "$STATUS" == "SUCCEEDED" ]]; then
    break
  elif [[ "$STATUS" == "FAILED" ]] || [[ "$STATUS" == "CANCELLED" ]]; then
    echo "Query failed: $STATUS"
    exit 1
  fi
  echo "Status: $STATUS, waiting..."
  sleep 2
done

# Get results
aws athena get-query-results --query-execution-id $QUERY_ID
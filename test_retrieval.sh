#!/bin/bash
declare -a QUERIES=(
  "I need a new battery"
  "My brakes are squealing"
  "Oil change service"
  "Tire replacement"
)

for query in "${QUERIES[@]}"; do
  echo "=========================================="
  echo "Query: $query"
  echo "=========================================="
  aws bedrock-agent-runtime retrieve \
    --knowledge-base-id UQSLM6QEVT \
    --retrieval-query text="$query" \
    --retrieval-configuration 'vectorSearchConfiguration={numberOfResults=1}' \
    --region us-east-1 \
    --output json | jq -r '.retrievalResults[0] | "Score: \(.score)\nFile: \(.location.s3Location.uri | split("/") | last)\nText: \(.content.text)\n"'
  echo ""
done

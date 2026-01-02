#!/bin/bash
# Test Bedrock Knowledge Base retrieval with various queries

KB_ID="UQSLM6QEVT"
REGION="us-east-1"
NUM_RESULTS="${1:-3}"

# Test queries covering different aspects of the project
declare -a QUERIES=(
  "What Glue ETL jobs exist in AutoCorp?"
  "How do I deploy DMS replication instance?"
  "What is the S3 bucket structure?"
  "How do I run unit tests?"
  "What are the analytics layer ETL jobs?"
  "How do I start a Glue job?"
  "What is the chunking configuration?"
  "Explain the data quality testing approach"
)

echo "=================================================="
echo "Testing Knowledge Base Retrieval"
echo "Knowledge Base ID: $KB_ID"
echo "Number of results per query: $NUM_RESULTS"
echo "=================================================="
echo ""

for query in "${QUERIES[@]}"; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 Query: $query"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  aws bedrock-agent-runtime retrieve \
    --knowledge-base-id "$KB_ID" \
    --retrieval-query text="$query" \
    --retrieval-configuration "vectorSearchConfiguration={numberOfResults=$NUM_RESULTS}" \
    --region "$REGION" \
    --output json | jq -r '
      .retrievalResults[] | 
      "
🎯 Score: \(.score)
📄 Source: \(.location.s3Location.uri // "N/A")
📝 Content Preview:
\(.content.text[0:300])...
      "
    '
  
  echo ""
done

echo "=================================================="
echo "✅ Testing Complete"
echo "=================================================="

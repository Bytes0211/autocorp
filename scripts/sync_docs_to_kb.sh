#!/bin/bash
# Sync documentation files to Bedrock Knowledge Base S3 location

set -e

BUCKET="autocorp-datalake-dev"
KB_PREFIX="knowledge-base/docs"

echo "Syncing documentation to s3://${BUCKET}/${KB_PREFIX}/"

# Upload project documentation
aws s3 cp WARP.md s3://${BUCKET}/${KB_PREFIX}/WARP.md
aws s3 cp README.md s3://${BUCKET}/${KB_PREFIX}/README.md
aws s3 cp project-status.md s3://${BUCKET}/${KB_PREFIX}/project-status.md
aws s3 cp TEST_README.md s3://${BUCKET}/${KB_PREFIX}/TEST_README.md
aws s3 cp PHASE5_AI_CHATBOX.md s3://${BUCKET}/${KB_PREFIX}/PHASE5_AI_CHATBOX.md
aws s3 cp PHASE5_QUICK_START.md s3://${BUCKET}/${KB_PREFIX}/PHASE5_QUICK_START.md

# Upload artifacts documentation
aws s3 cp artifacts/developer_approach.md s3://${BUCKET}/${KB_PREFIX}/artifacts/developer_approach.md
aws s3 cp artifacts/DATA_QUALITY_TESTING.md s3://${BUCKET}/${KB_PREFIX}/artifacts/DATA_QUALITY_TESTING.md
aws s3 cp artifacts/DATA_QUALITY_QUICK_REFERENCE.md s3://${BUCKET}/${KB_PREFIX}/artifacts/DATA_QUALITY_QUICK_REFERENCE.md

# Upload terraform docs
aws s3 cp terraform/README.md s3://${BUCKET}/${KB_PREFIX}/terraform/README.md
aws s3 cp terraform/modules/athena/README.md s3://${BUCKET}/${KB_PREFIX}/terraform/modules/athena/README.md
aws s3 cp terraform/modules/dms/README.md s3://${BUCKET}/${KB_PREFIX}/terraform/modules/dms/README.md

# Upload docs folder
aws s3 sync docs/ s3://${BUCKET}/${KB_PREFIX}/docs/ \
  --exclude "*.png" \
  --exclude "*.jpg" \
  --exclude "*.gif"

# Upload key ETL scripts (for reference)
aws s3 sync terraform/modules/glue/scripts/ s3://${BUCKET}/${KB_PREFIX}/glue-scripts/ \
  --include "*.py"

echo "✅ Documentation sync complete!"
echo ""
echo "Next steps:"
echo "1. Start ingestion job:"
echo "   aws bedrock-agent start-ingestion-job --knowledge-base-id UQSLM6QEVT --data-source-id GWCPMZICOY --region us-east-1"
echo ""
echo "2. Check ingestion status:"
echo "   aws bedrock-agent list-ingestion-jobs --knowledge-base-id UQSLM6QEVT --data-source-id GWCPMZICOY --region us-east-1"

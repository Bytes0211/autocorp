# Bedrock Module - Knowledge Base with OpenSearch Serverless for RAG
# This module creates AWS Bedrock infrastructure for AI chatbox with RAG capabilities

# Data source for current AWS region
data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

# OpenSearch Serverless Collection for vector store
resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${var.project_name}-kb-encryption-${var.environment}"
  type = "encryption"
  
  policy = jsonencode({
    Rules = [{
      Resource = [
        "collection/${var.project_name}-kb-${var.environment}"
      ]
      ResourceType = "collection"
    }]
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name = "${var.project_name}-kb-network-${var.environment}"
  type = "network"
  
  policy = jsonencode([{
    Rules = [{
      Resource = [
        "collection/${var.project_name}-kb-${var.environment}"
      ]
      ResourceType = "collection"
    }]
    AllowFromPublic = true
  }])
}

resource "aws_opensearchserverless_collection" "knowledge_base" {
  name = "${var.project_name}-kb-${var.environment}"
  type = "VECTORSEARCH"
  
  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network
  ]
  
  tags = {
    Name        = "${var.project_name}-kb-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "Bedrock Knowledge Base Vector Store"
  }
}

# IAM role for Bedrock to access OpenSearch and S3
resource "aws_iam_role" "bedrock_kb" {
  name = "${var.project_name}-bedrock-kb-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "bedrock.amazonaws.com"
      }
    }]
  })
  
  tags = {
    Name        = "${var.project_name}-bedrock-kb-role-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM policy for Bedrock to access S3 knowledge base data
resource "aws_iam_role_policy" "bedrock_kb_s3" {
  name = "s3-access"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        "${var.knowledge_base_bucket_arn}",
        "${var.knowledge_base_bucket_arn}/*"
      ]
    }]
  })
}

# IAM policy for Bedrock to access OpenSearch Serverless
resource "aws_iam_role_policy" "bedrock_kb_aoss" {
  name = "opensearch-access"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "aoss:APIAccessAll"
      ]
      Resource = [
        aws_opensearchserverless_collection.knowledge_base.arn
      ]
    }]
  })
}

# IAM policy for Bedrock model access
resource "aws_iam_role_policy" "bedrock_kb_models" {
  name = "bedrock-models"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "bedrock:InvokeModel"
      ]
      Resource = [
        "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.embedding_model}"
      ]
    }]
  })
}

# Data access policy for OpenSearch (created after IAM role)
resource "aws_opensearchserverless_access_policy" "knowledge_base" {
  name = "${var.project_name}-kb-access-${var.environment}"
  type = "data"
  
  policy = jsonencode([{
    Rules = [{
      Resource = [
        "collection/${var.project_name}-kb-${var.environment}"
      ]
      Permission = [
        "aoss:CreateCollectionItems",
        "aoss:DeleteCollectionItems",
        "aoss:UpdateCollectionItems",
        "aoss:DescribeCollectionItems"
      ]
      ResourceType = "collection"
    }, {
      Resource = [
        "index/${var.project_name}-kb-${var.environment}/*"
      ]
      Permission = [
        "aoss:CreateIndex",
        "aoss:DeleteIndex",
        "aoss:UpdateIndex",
        "aoss:DescribeIndex",
        "aoss:ReadDocument",
        "aoss:WriteDocument"
      ]
      ResourceType = "index"
    }]
    Principal = [
      aws_iam_role.bedrock_kb.arn,
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/cottondev"
    ]
  }])
  
  depends_on = [
    aws_iam_role.bedrock_kb
  ]
}

# Bedrock Knowledge Base
resource "aws_bedrockagent_knowledge_base" "autocorp" {
  name     = "${var.project_name}-kb-${var.environment}"
  role_arn = aws_iam_role.bedrock_kb.arn
  
  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.embedding_model}"
    }
  }
  
  storage_configuration {
    type = "OPENSEARCH_SERVERLESS"
    opensearch_serverless_configuration {
      collection_arn    = aws_opensearchserverless_collection.knowledge_base.arn
      vector_index_name = "bedrock-knowledge-base-default-index"
      field_mapping {
        vector_field   = "bedrock-knowledge-base-default-vector"
        text_field     = "AMAZON_BEDROCK_TEXT_CHUNK"
        metadata_field = "AMAZON_BEDROCK_METADATA"
      }
    }
  }
  
  depends_on = [
    aws_opensearchserverless_collection.knowledge_base,
    aws_opensearchserverless_access_policy.knowledge_base,
    aws_iam_role_policy.bedrock_kb_s3,
    aws_iam_role_policy.bedrock_kb_aoss,
    aws_iam_role_policy.bedrock_kb_models
  ]
  
  tags = {
    Name        = "${var.project_name}-kb-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Bedrock Knowledge Base Data Source
resource "aws_bedrockagent_data_source" "autocorp" {
  count              = var.enable_data_source ? 1 : 0
  knowledge_base_id  = aws_bedrockagent_knowledge_base.autocorp.id
  name               = "${var.project_name}-kb-datasource-${var.environment}"
  
  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = var.knowledge_base_bucket_arn
      inclusion_prefixes = [
        "knowledge-base/"
      ]
    }
  }
  
  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "FIXED_SIZE"
      fixed_size_chunking_configuration {
        max_tokens         = var.chunk_size_tokens
        overlap_percentage = var.chunk_overlap_percentage
      }
    }
  }
}

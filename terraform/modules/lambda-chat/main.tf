# Lambda Chat Module - Lambda Functions + API Gateway for AutoCorp AI Chatbox
# Includes: Lambda functions, IAM roles, API Gateway REST API, and API keys

# ===========================
# IAM Role for Chat Handler Lambda
# ===========================

resource "aws_iam_role" "chat_handler" {
  name = "${var.project_name}-chat-handler-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "${var.project_name}-chat-handler-role-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# IAM Policy for Chat Handler - Bedrock and Knowledge Base access
resource "aws_iam_role_policy" "chat_handler_bedrock" {
  name = "${var.project_name}-chat-handler-bedrock-${var.environment}"
  role = aws_iam_role.chat_handler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-pro-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v1"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:Retrieve",
          "bedrock:RetrieveAndGenerate"
        ]
        Resource = var.knowledge_base_arn
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:GetKnowledgeBase"
        ]
        Resource = var.knowledge_base_arn
      },
      {
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-chat-handler-${var.environment}:*"
      }
    ]
  })
}

# ===========================
# IAM Role for Analytics Query Lambda
# ===========================

resource "aws_iam_role" "analytics_query" {
  name = "${var.project_name}-analytics-query-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "${var.project_name}-analytics-query-role-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# IAM Policy for Analytics Query - Athena and Glue access
resource "aws_iam_role_policy" "analytics_query_athena" {
  name = "${var.project_name}-analytics-query-athena-${var.environment}"
  role = aws_iam_role.analytics_query.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution"
        ]
        Resource = [
          "arn:aws:athena:${var.aws_region}:*:workgroup/${var.athena_workgroup}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartitions"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",
          "s3:GetBucketLocation"
        ]
        Resource = [
          "${var.s3_bucket_arn}",
          "${var.s3_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-analytics-query-${var.environment}:*"
      }
    ]
  })
}

# ===========================
# Lambda Functions
# ===========================

# Package Lambda functions as ZIP files
data "archive_file" "chat_handler" {
  type        = "zip"
  source_dir  = "${path.root}/../lambda/chat-handler"
  output_path = "${path.root}/.terraform/lambda/chat-handler.zip"
}

data "archive_file" "analytics_query" {
  type        = "zip"
  source_dir  = "${path.root}/../lambda/analytics-query"
  output_path = "${path.root}/.terraform/lambda/analytics-query.zip"
}

# Chat Handler Lambda Function
resource "aws_lambda_function" "chat_handler" {
  filename         = data.archive_file.chat_handler.output_path
  function_name    = "${var.project_name}-chat-handler-${var.environment}"
  role            = aws_iam_role.chat_handler.arn
  handler         = "handler.lambda_handler"
  source_code_hash = data.archive_file.chat_handler.output_base64sha256
  runtime         = "python3.12"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = var.knowledge_base_id
      MODEL_ID         = "amazon.nova-pro-v1:0"
      MAX_RESULTS      = "5"
      MAX_TOKENS       = "500"
      TEMPERATURE      = "0.7"
    }
  }

  tags = {
    Name        = "${var.project_name}-chat-handler-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Analytics Query Lambda Function
resource "aws_lambda_function" "analytics_query" {
  filename         = data.archive_file.analytics_query.output_path
  function_name    = "${var.project_name}-analytics-query-${var.environment}"
  role            = aws_iam_role.analytics_query.arn
  handler         = "handler.lambda_handler"
  source_code_hash = data.archive_file.analytics_query.output_base64sha256
  runtime         = "python3.12"
  timeout         = 60
  memory_size     = 256

  environment {
    variables = {
      DATABASE_NAME    = var.glue_database
      OUTPUT_LOCATION  = "s3://${var.s3_bucket_name}/athena-results/"
      WORKGROUP        = var.athena_workgroup
      MAX_WAIT_TIME    = "30"
    }
  }

  tags = {
    Name        = "${var.project_name}-analytics-query-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "chat_handler" {
  name              = "/aws/lambda/${aws_lambda_function.chat_handler.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-chat-handler-logs-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "analytics_query" {
  name              = "/aws/lambda/${aws_lambda_function.analytics_query.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-analytics-query-logs-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ===========================
# API Gateway REST API
# ===========================

resource "aws_api_gateway_rest_api" "chatbox" {
  name        = "${var.project_name}-chatbox-api-${var.environment}"
  description = "AutoCorp AI Chatbox API for chat and analytics queries"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.project_name}-chatbox-api-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ===========================
# /chat Resource and Methods
# ===========================

resource "aws_api_gateway_resource" "chat" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  parent_id   = aws_api_gateway_rest_api.chatbox.root_resource_id
  path_part   = "chat"
}

# POST /chat method
resource "aws_api_gateway_method" "chat_post" {
  rest_api_id   = aws_api_gateway_rest_api.chatbox.id
  resource_id   = aws_api_gateway_resource.chat.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = true
}

# Lambda integration for POST /chat
resource "aws_api_gateway_integration" "chat_post" {
  rest_api_id             = aws_api_gateway_rest_api.chatbox.id
  resource_id             = aws_api_gateway_resource.chat.id
  http_method             = aws_api_gateway_method.chat_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.chat_handler.invoke_arn
}

# OPTIONS /chat method for CORS
resource "aws_api_gateway_method" "chat_options" {
  rest_api_id   = aws_api_gateway_rest_api.chatbox.id
  resource_id   = aws_api_gateway_resource.chat.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# CORS integration for OPTIONS /chat
resource "aws_api_gateway_integration" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = aws_api_gateway_method_response.chat_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Api-Key'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# ===========================
# /analytics Resource and Methods
# ===========================

resource "aws_api_gateway_resource" "analytics" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  parent_id   = aws_api_gateway_rest_api.chatbox.root_resource_id
  path_part   = "analytics"
}

# POST /analytics method
resource "aws_api_gateway_method" "analytics_post" {
  rest_api_id   = aws_api_gateway_rest_api.chatbox.id
  resource_id   = aws_api_gateway_resource.analytics.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = true
}

# Lambda integration for POST /analytics
resource "aws_api_gateway_integration" "analytics_post" {
  rest_api_id             = aws_api_gateway_rest_api.chatbox.id
  resource_id             = aws_api_gateway_resource.analytics.id
  http_method             = aws_api_gateway_method.analytics_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.analytics_query.invoke_arn
}

# OPTIONS /analytics method for CORS
resource "aws_api_gateway_method" "analytics_options" {
  rest_api_id   = aws_api_gateway_rest_api.chatbox.id
  resource_id   = aws_api_gateway_resource.analytics.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# CORS integration for OPTIONS /analytics
resource "aws_api_gateway_integration" "analytics_options" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  resource_id = aws_api_gateway_resource.analytics.id
  http_method = aws_api_gateway_method.analytics_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "analytics_options" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  resource_id = aws_api_gateway_resource.analytics.id
  http_method = aws_api_gateway_method.analytics_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "analytics_options" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id
  resource_id = aws_api_gateway_resource.analytics.id
  http_method = aws_api_gateway_method.analytics_options.http_method
  status_code = aws_api_gateway_method_response.analytics_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Api-Key'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# ===========================
# Lambda Permissions for API Gateway
# ===========================

resource "aws_lambda_permission" "chat_handler_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.chatbox.execution_arn}/*/*"
}

resource "aws_lambda_permission" "analytics_query_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics_query.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.chatbox.execution_arn}/*/*"
}

# ===========================
# API Gateway Deployment
# ===========================

resource "aws_api_gateway_deployment" "chatbox" {
  rest_api_id = aws_api_gateway_rest_api.chatbox.id

  # Force new deployment on any API change
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.chat.id,
      aws_api_gateway_method.chat_post.id,
      aws_api_gateway_integration.chat_post.id,
      aws_api_gateway_resource.analytics.id,
      aws_api_gateway_method.analytics_post.id,
      aws_api_gateway_integration.analytics_post.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.chat_post,
    aws_api_gateway_integration.analytics_post,
    aws_api_gateway_integration.chat_options,
    aws_api_gateway_integration.analytics_options
  ]
}

resource "aws_api_gateway_stage" "chatbox" {
  deployment_id = aws_api_gateway_deployment.chatbox.id
  rest_api_id   = aws_api_gateway_rest_api.chatbox.id
  stage_name    = var.environment

  tags = {
    Name        = "${var.project_name}-chatbox-api-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ===========================
# API Key and Usage Plan
# ===========================

resource "aws_api_gateway_api_key" "chatbox" {
  name    = "${var.project_name}-chatbox-api-key-${var.environment}"
  enabled = true

  tags = {
    Name        = "${var.project_name}-chatbox-api-key-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_api_gateway_usage_plan" "chatbox" {
  name        = "${var.project_name}-chatbox-usage-plan-${var.environment}"
  description = "Usage plan for AutoCorp AI Chatbox API"

  api_stages {
    api_id = aws_api_gateway_rest_api.chatbox.id
    stage  = aws_api_gateway_stage.chatbox.stage_name
  }

  quota_settings {
    limit  = 10000
    period = "MONTH"
  }

  throttle_settings {
    burst_limit = 50
    rate_limit  = 100
  }

  tags = {
    Name        = "${var.project_name}-chatbox-usage-plan-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_api_gateway_usage_plan_key" "chatbox" {
  key_id        = aws_api_gateway_api_key.chatbox.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.chatbox.id
}

# ===========================
# Store API Key in Secrets Manager
# ===========================

resource "aws_secretsmanager_secret" "api_key" {
  name        = "${var.project_name}/${var.environment}/chatbox-api-key"
  description = "API key for AutoCorp AI Chatbox"

  tags = {
    Name        = "${var.project_name}-chatbox-api-key-secret-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "api_key" {
  secret_id     = aws_secretsmanager_secret.api_key.id
  secret_string = aws_api_gateway_api_key.chatbox.value
}

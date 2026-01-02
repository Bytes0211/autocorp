# Lambda Function Outputs
output "chat_handler_function_name" {
  description = "Name of the chat handler Lambda function"
  value       = aws_lambda_function.chat_handler.function_name
}

output "chat_handler_function_arn" {
  description = "ARN of the chat handler Lambda function"
  value       = aws_lambda_function.chat_handler.arn
}

output "analytics_query_function_name" {
  description = "Name of the analytics query Lambda function"
  value       = aws_lambda_function.analytics_query.function_name
}

output "analytics_query_function_arn" {
  description = "ARN of the analytics query Lambda function"
  value       = aws_lambda_function.analytics_query.arn
}

# API Gateway Outputs
output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.chatbox.id
}

output "api_gateway_endpoint" {
  description = "Invoke URL for the API Gateway"
  value       = "${aws_api_gateway_stage.chatbox.invoke_url}"
}

output "api_gateway_stage_name" {
  description = "Name of the API Gateway stage"
  value       = aws_api_gateway_stage.chatbox.stage_name
}

# API Key Outputs
output "api_key_id" {
  description = "ID of the API Gateway API key"
  value       = aws_api_gateway_api_key.chatbox.id
}

output "api_key_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the API key"
  value       = aws_secretsmanager_secret.api_key.arn
}

# Endpoint URLs
output "chat_endpoint" {
  description = "Full URL for the chat endpoint"
  value       = "${aws_api_gateway_stage.chatbox.invoke_url}/chat"
}

output "analytics_endpoint" {
  description = "Full URL for the analytics endpoint"
  value       = "${aws_api_gateway_stage.chatbox.invoke_url}/analytics"
}

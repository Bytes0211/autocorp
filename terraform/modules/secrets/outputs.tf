# Secrets Module Outputs

output "postgres_password_secret_arn" {
  description = "ARN of the PostgreSQL password secret"
  value       = aws_secretsmanager_secret.postgres_password.arn
}

output "postgres_password_secret_name" {
  description = "Name of the PostgreSQL password secret"
  value       = aws_secretsmanager_secret.postgres_password.name
}

output "postgres_password_secret_description" {
  description = "Description of the PostgreSQL password secret"
  value       = aws_secretsmanager_secret.postgres_password.description
}

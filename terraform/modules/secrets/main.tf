# Secrets Manager Module
# Creates AWS Secrets Manager secret for PostgreSQL password

resource "aws_secretsmanager_secret" "postgres_password" {
  name        = "${var.project_name}/${var.environment}/postgres/password"
  description = "PostgreSQL password for DMS replication"

  tags = {
    Name = "${var.project_name}-postgres-password-${var.environment}"
  }
}

# Note: The actual secret value must be manually set via:
# aws secretsmanager put-secret-value \
#   --secret-id <secret-arn> \
#   --secret-string <password>

# AutoCorp Data Lake Pipeline - Backend Configuration
# 
# IMPORTANT: Before using this backend, you must manually create:
# 1. S3 bucket: autocorp-terraform-state-<account-id>
# 2. DynamoDB table: autocorp-terraform-locks
#
# To initialize:
# terraform init -backend-config="bucket=autocorp-terraform-state-<your-account-id>"

terraform {
  backend "s3" {
    # S3 bucket for Terraform state (with AWS account ID for uniqueness)
    bucket = "autocorp-terraform-state-696056865313"
    key    = "datalake/terraform.tfstate"
    region = "us-east-1"
    
    # State locking via DynamoDB
    dynamodb_table = "autocorp-terraform-locks"
    
    # Encryption and versioning
    encrypt = true
    
    # Workspace support
    workspace_key_prefix = "workspaces"
  }
}

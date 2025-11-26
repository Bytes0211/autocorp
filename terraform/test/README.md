# AutoCorp Terraform Tests

This directory contains automated unit and integration tests for the AutoCorp Terraform infrastructure using [Terratest](https://terratest.gruntwork.io/).

## Overview

The test suite validates the following:

1. **S3 Module Tests** (`s3_test.go`)
   - Data lake bucket creation with versioning enabled
   - Encryption configuration (AES256)
   - Public access blocking
   - Lifecycle policies for data archival

2. **IAM Module Tests** (`iam_test.go`)
   - Glue IAM role with correct assume role policy
   - DMS IAM role with scoped S3 permissions
   - DataSync IAM role with scoped S3 permissions
   - Inline policies for each service role

3. **Glue Module Tests** (`glue_test.go`)
   - Data Catalog database creation
   - Crawler configuration with correct S3 targets
   - Crawler schedules
   - Schema change policies

4. **Secrets & Conditional Module Tests** (`secrets_and_conditional_test.go`)
   - Secrets Manager configuration with proper naming
   - DMS module conditional creation based on `enable_dms` variable
   - DataSync module conditional creation based on `enable_datasync` variable

## Prerequisites

### Required Tools

- Go 1.21 or higher
- Terraform 1.5.0 or higher
- AWS CLI configured with credentials
- AWS account with permissions to create test resources

### AWS Permissions

The test suite will create and destroy real AWS resources. Ensure your AWS credentials have permissions for:
- S3 (buckets, versioning, encryption, lifecycle)
- IAM (roles, policies)
- Glue (catalogs, crawlers)
- Secrets Manager

### Cost Considerations

Running these tests will incur minimal AWS costs (typically < $1 per full test run). Tests use `defer terraform.Destroy()` to clean up resources, but verify cleanup to avoid unexpected charges.

## Installation

1. Initialize Go modules:
```bash
cd terraform/test
go mod init github.com/autocorp/terraform-tests
go mod tidy
```

2. Download dependencies:
```bash
go get github.com/gruntwork-io/terratest/modules/terraform
go get github.com/stretchr/testify/assert
```

## Running Tests

### Run All Tests
```bash
cd terraform/test
go test -v -timeout 30m
```

### Run Specific Test
```bash
# Run S3 tests only
go test -v -timeout 30m -run TestS3

# Run IAM tests only
go test -v -timeout 30m -run TestIAM

# Run Glue tests only
go test -v -timeout 30m -run TestGlue

# Run a single test function
go test -v -timeout 30m -run TestS3DataLakeBucketConfiguration
```

### Run Tests in Parallel
Tests are configured to run in parallel for faster execution:
```bash
go test -v -timeout 30m -parallel 4
```

### Run Tests with Coverage
```bash
go test -v -timeout 30m -cover -coverprofile=coverage.out
go tool cover -html=coverage.out -o coverage.html
```

## Test Structure

Each test follows this pattern:

1. **Setup**: Configure Terraform options with test-specific variables
2. **Defer Cleanup**: Schedule resource destruction with `defer terraform.Destroy()`
3. **Apply**: Run `terraform init` and `terraform apply`
4. **Assert**: Validate outputs and resource configurations
5. **Cleanup**: Automatic cleanup via deferred destroy

Example:
```go
func TestS3DataLakeBucketConfiguration(t *testing.T) {
    t.Parallel()
    
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../",
        Vars: map[string]interface{}{
            "project_name": "autocorp-test",
            "environment":  "dev",
        },
        Targets: []string{"module.s3"},
    })
    
    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)
    
    // Assertions
    bucketName := terraform.Output(t, terraformOptions, "data_lake_bucket_id")
    assert.NotEmpty(t, bucketName)
}
```

## Test Configuration

### Unique Resource Names
Each test uses unique project names to avoid conflicts:
- `autocorp-test` for basic tests
- `autocorp-test-glue`, `autocorp-test-dms`, etc. for specific tests

### Targeted Testing
Tests use `Targets` to deploy only necessary modules, reducing test time:
```go
Targets: []string{"module.s3", "module.iam"}
```

### Conditional Module Testing
For DMS and DataSync (which require external dependencies), tests verify:
- Modules are NOT created when disabled (default)
- Modules WOULD be created when enabled (via plan validation)

## Troubleshooting

### Test Timeouts
If tests timeout, increase the timeout value:
```bash
go test -v -timeout 60m
```

### Resource Cleanup Failures
If tests fail and leave resources behind:
```bash
# List remaining resources
aws s3 ls | grep autocorp-test

# Manual cleanup
aws s3 rb s3://autocorp-test-xyz --force
```

### AWS Credentials
Ensure AWS credentials are configured:
```bash
aws configure list
aws sts get-caller-identity
```

### Backend State Conflicts
Tests use local state (no backend) to avoid conflicts. If you see state locking errors, check for leftover `.terraform` directories:
```bash
find terraform/test -name ".terraform" -type d -exec rm -rf {} +
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Always use `defer terraform.Destroy()` to ensure cleanup
3. **Unique Names**: Use unique project names to avoid resource conflicts
4. **Parallel Safety**: Tests marked with `t.Parallel()` must not share resources
5. **Cost Awareness**: Be mindful of AWS costs; use smallest instance types

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Terraform Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: '1.5.0'
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Run Tests
        run: |
          cd terraform/test
          go mod download
          go test -v -timeout 30m
```

## References

- [Terratest Documentation](https://terratest.gruntwork.io/)
- [Terraform Testing Best Practices](https://www.terraform.io/docs/language/modules/testing-experiment.html)
- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## Support

For issues or questions:
1. Check test output for specific error messages
2. Verify AWS credentials and permissions
3. Review Terraform state for resource conflicts
4. Consult the main [Terraform README](../README.md)

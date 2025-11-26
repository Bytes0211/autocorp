# Quick Start Guide - Terraform Tests

## First Time Setup

```bash
# 1. Navigate to test directory
cd terraform/test

# 2. Install Go (if not already installed)
# Ubuntu/Debian:
sudo apt install golang-go

# macOS:
brew install go

# 3. Initialize Go modules
make init

# 4. Verify AWS credentials
aws sts get-caller-identity
```

## Running Tests

```bash
# Run all tests (sequential)
make test

# Run all tests (parallel - faster)
make test-parallel

# Run specific module tests
make test-s3           # S3 bucket tests
make test-iam          # IAM role tests
make test-glue         # Glue catalog tests
make test-secrets      # Secrets Manager tests
make test-conditional  # Conditional module tests

# Generate coverage report
make coverage
```

## Test Results Interpretation

### ✅ Success Output
```
=== RUN   TestS3DataLakeBucketConfiguration
--- PASS: TestS3DataLakeBucketConfiguration (45.23s)
PASS
ok      github.com/autocorp/terraform-tests    45.234s
```

### ❌ Failure Output
```
=== RUN   TestS3DataLakeBucketConfiguration
    s3_test.go:36: Bucket versioning should be enabled
--- FAIL: TestS3DataLakeBucketConfiguration (45.23s)
FAIL
```

## Common Issues

### Issue: AWS Credentials Not Found
```bash
# Solution: Configure AWS CLI
aws configure
```

### Issue: Tests Timeout
```bash
# Solution: Increase timeout
go test -v -timeout 60m
```

### Issue: Resources Not Cleaned Up
```bash
# Solution: Manually clean up
aws s3 ls | grep autocorp-test
aws s3 rb s3://autocorp-test-xyz --force

# Or use make clean
make clean
```

## Cost Management

- Each test run: < $1
- Most costs from S3 storage (minimal)
- Resources auto-deleted after tests
- Monitor AWS billing console to verify cleanup

## Next Steps

1. ✅ Run tests locally to verify setup
2. ✅ Integrate tests into CI/CD pipeline
3. ✅ Add tests for new Terraform resources
4. ✅ Review test output regularly

## Help

```bash
# Show available commands
make help

# View detailed documentation
cat README.md
```

## Contact

For issues or questions, see:
- Detailed README: `test/README.md`
- Test Summary: `TEST_SUITE_SUMMARY.md`
- Main Terraform docs: `terraform/README.md`

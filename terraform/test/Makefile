.PHONY: help init test test-s3 test-iam test-glue test-secrets test-conditional test-parallel clean coverage

# Default target
help:
	@echo "AutoCorp Terraform Test Suite"
	@echo ""
	@echo "Available targets:"
	@echo "  init              - Initialize Go modules and download dependencies"
	@echo "  test              - Run all tests sequentially"
	@echo "  test-s3           - Run S3 module tests only"
	@echo "  test-iam          - Run IAM module tests only"
	@echo "  test-glue         - Run Glue module tests only"
	@echo "  test-secrets      - Run Secrets Manager tests only"
	@echo "  test-conditional  - Run conditional module creation tests only"
	@echo "  test-parallel     - Run all tests in parallel (faster)"
	@echo "  coverage          - Run tests with coverage report"
	@echo "  clean             - Clean up test artifacts and temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make init         # First time setup"
	@echo "  make test         # Run all tests"
	@echo "  make test-s3      # Run S3 tests only"

# Initialize Go modules and dependencies
init:
	@echo "Initializing Go modules..."
	go mod tidy
	go mod download
	@echo "Dependencies installed successfully!"

# Run all tests with standard timeout
test:
	@echo "Running all Terraform tests..."
	go test -v -timeout 30m

# Run S3 module tests
test-s3:
	@echo "Running S3 module tests..."
	go test -v -timeout 30m -run TestS3

# Run IAM module tests
test-iam:
	@echo "Running IAM module tests..."
	go test -v -timeout 30m -run TestIAM -run TestGlue -run TestDMS -run TestDataSync

# Run Glue module tests
test-glue:
	@echo "Running Glue module tests..."
	go test -v -timeout 30m -run TestGlue

# Run Secrets Manager tests
test-secrets:
	@echo "Running Secrets Manager tests..."
	go test -v -timeout 30m -run TestSecretsManager

# Run conditional module creation tests
test-conditional:
	@echo "Running conditional module tests..."
	go test -v -timeout 30m -run TestDMSModuleConditional -run TestDataSyncModuleConditional -run TestConditionalModulesIndependence

# Run all tests in parallel for faster execution
test-parallel:
	@echo "Running all tests in parallel..."
	go test -v -timeout 30m -parallel 4

# Run tests with coverage report
coverage:
	@echo "Running tests with coverage analysis..."
	go test -v -timeout 30m -cover -coverprofile=coverage.out
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

# Clean up test artifacts
clean:
	@echo "Cleaning up test artifacts..."
	rm -f coverage.out coverage.html
	rm -rf .terraform
	rm -f terraform.tfstate*
	rm -f .terraform.lock.hcl
	@echo "Cleanup complete!"

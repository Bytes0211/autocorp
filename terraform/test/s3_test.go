package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

// TestS3DataLakeBucketConfiguration tests that the S3 data lake bucket is created
// with versioning, encryption, and public access blocked
func TestS3DataLakeBucketConfiguration(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":         "autocorp-test",
			"environment":          "dev",
			"enable_s3_versioning": true,
			"enable_dms":           false,
			"enable_datasync":      false,
		},
		Targets: []string{"module.s3"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Get bucket name from output
	bucketName := terraform.Output(t, terraformOptions, "data_lake_bucket_id")
	assert.NotEmpty(t, bucketName, "Bucket name should not be empty")

	// Verify bucket versioning is enabled
	versioningStatus := terraform.OutputMap(t, terraformOptions, "s3_bucket_versioning")
	assert.Equal(t, "Enabled", versioningStatus["status"], "Bucket versioning should be enabled")

	// Verify encryption is configured
	encryptionConfig := terraform.OutputMap(t, terraformOptions, "s3_bucket_encryption")
	assert.Equal(t, "AES256", encryptionConfig["sse_algorithm"], "Bucket should use AES256 encryption")

	// Verify public access is blocked
	publicAccessBlock := terraform.OutputMap(t, terraformOptions, "s3_public_access_block")
	assert.Equal(t, "true", publicAccessBlock["block_public_acls"], "Public ACLs should be blocked")
	assert.Equal(t, "true", publicAccessBlock["block_public_policy"], "Public policies should be blocked")
	assert.Equal(t, "true", publicAccessBlock["ignore_public_acls"], "Public ACLs should be ignored")
	assert.Equal(t, "true", publicAccessBlock["restrict_public_buckets"], "Public buckets should be restricted")
}

// TestS3BucketVersioningCanBeDisabled tests that versioning can be disabled
func TestS3BucketVersioningCanBeDisabled(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":         "autocorp-test-novs",
			"environment":          "dev",
			"enable_s3_versioning": false,
			"enable_dms":           false,
			"enable_datasync":      false,
		},
		Targets: []string{"module.s3"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify bucket versioning is suspended
	versioningStatus := terraform.OutputMap(t, terraformOptions, "s3_bucket_versioning")
	assert.Equal(t, "Suspended", versioningStatus["status"], "Bucket versioning should be suspended")
}

// TestS3LifecycleConfiguration tests that lifecycle policies are correctly configured
func TestS3LifecycleConfiguration(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":      "autocorp-test-lc",
			"environment":       "dev",
			"s3_lifecycle_days": 30,
			"enable_dms":        false,
			"enable_datasync":   false,
		},
		Targets: []string{"module.s3"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify lifecycle configuration
	lifecycleConfig := terraform.OutputMap(t, terraformOptions, "s3_lifecycle_rules")
	assert.Contains(t, lifecycleConfig, "archive-raw-zone", "Should have archive-raw-zone rule")
	assert.Contains(t, lifecycleConfig, "expire-logs", "Should have expire-logs rule")
}

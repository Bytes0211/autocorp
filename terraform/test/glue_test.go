package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

// TestGlueCatalogDatabase tests that the Glue Data Catalog database is created
func TestGlueCatalogDatabase(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":        "autocorp-test-catalog",
			"environment":         "dev",
			"enable_glue_crawlers": false,
			"enable_dms":          false,
			"enable_datasync":     false,
		},
		Targets: []string{"module.s3", "module.iam", "module.glue"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify catalog database name
	catalogDbName := terraform.Output(t, terraformOptions, "glue_catalog_database_name")
	assert.Equal(t, "autocorp-test-catalog_dev", catalogDbName, "Catalog database should follow naming convention")

	// Verify catalog database description
	catalogDbDescription := terraform.Output(t, terraformOptions, "glue_catalog_database_description")
assert.Contains(t, catalogDbDescription, "AutoCorp", "Catalog database should have appropriate description")
}

// TestGlueCrawlersConfiguration tests that Glue crawlers are correctly configured
// with the specified S3 targets and schedules
func TestGlueCrawlersConfiguration(t *testing.T) {
	t.Parallel()

	crawlerSchedule := "cron(0 3 * * ? *)" // 3 AM UTC

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":         "autocorp-test-crawlers",
			"environment":          "dev",
			"enable_glue_crawlers": true,
			"glue_crawler_schedule": crawlerSchedule,
			"enable_dms":           false,
			"enable_datasync":      false,
		},
		Targets: []string{"module.s3", "module.iam", "module.glue"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify raw database crawler name
	rawDbCrawlerName := terraform.Output(t, terraformOptions, "glue_raw_database_crawler_name")
	expectedRawDbName := "autocorp-test-crawlers-raw-database-crawler-dev"
	assert.Equal(t, expectedRawDbName, rawDbCrawlerName, "Raw database crawler should follow naming convention")

	// Verify raw CSV crawler name
	rawCsvCrawlerName := terraform.Output(t, terraformOptions, "glue_raw_csv_crawler_name")
	expectedRawCsvName := "autocorp-test-crawlers-raw-csv-crawler-dev"
	assert.Equal(t, expectedRawCsvName, rawCsvCrawlerName, "Raw CSV crawler should follow naming convention")

	// Verify crawler schedule
	rawDbSchedule := terraform.Output(t, terraformOptions, "glue_raw_database_crawler_schedule")
	assert.Equal(t, crawlerSchedule, rawDbSchedule, "Raw database crawler should use specified schedule")

	rawCsvSchedule := terraform.Output(t, terraformOptions, "glue_raw_csv_crawler_schedule")
	assert.Equal(t, crawlerSchedule, rawCsvSchedule, "Raw CSV crawler should use specified schedule")

	// Verify crawler S3 targets
	rawDbTarget := terraform.Output(t, terraformOptions, "glue_raw_database_crawler_target")
	bucketName := terraform.Output(t, terraformOptions, "data_lake_bucket_id")
	expectedDbTarget := fmt.Sprintf("s3://%s/raw/database/", bucketName)
	assert.Equal(t, expectedDbTarget, rawDbTarget, "Raw database crawler should target raw/database/")

	rawCsvTarget := terraform.Output(t, terraformOptions, "glue_raw_csv_crawler_target")
	expectedCsvTarget := fmt.Sprintf("s3://%s/raw/csv/", bucketName)
	assert.Equal(t, expectedCsvTarget, rawCsvTarget, "Raw CSV crawler should target raw/csv/")

	// Verify schema change policy
	rawDbSchemaPolicy := terraform.OutputMap(t, terraformOptions, "glue_raw_database_crawler_schema_policy")
	assert.Equal(t, "LOG", rawDbSchemaPolicy["delete_behavior"], "Delete behavior should be LOG")
	assert.Equal(t, "UPDATE_IN_DATABASE", rawDbSchemaPolicy["update_behavior"], "Update behavior should be UPDATE_IN_DATABASE")
}

// TestGlueCrawlersDisabled tests that crawlers are not created when disabled
func TestGlueCrawlersDisabled(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":         "autocorp-test-no-crawlers",
			"environment":          "dev",
			"enable_glue_crawlers": false,
			"enable_dms":           false,
			"enable_datasync":      false,
		},
		Targets: []string{"module.s3", "module.iam", "module.glue"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify crawlers are not created
	outputs := terraform.OutputAll(t, terraformOptions)
	
	// Check that crawler outputs don't exist or are empty
	_, rawDbCrawlerExists := outputs["glue_raw_database_crawler_name"]
	assert.False(t, rawDbCrawlerExists, "Raw database crawler should not be created when disabled")

	_, rawCsvCrawlerExists := outputs["glue_raw_csv_crawler_name"]
	assert.False(t, rawCsvCrawlerExists, "Raw CSV crawler should not be created when disabled")
}

// TestGlueCrawlerRoleAssignment tests that crawlers use the correct IAM role
func TestGlueCrawlerRoleAssignment(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":         "autocorp-test-role",
			"environment":          "dev",
			"enable_glue_crawlers": true,
			"enable_dms":           false,
			"enable_datasync":      false,
		},
		Targets: []string{"module.s3", "module.iam", "module.glue"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Get Glue role ARN
	glueRoleArn := terraform.Output(t, terraformOptions, "glue_role_arn")
	
	// Verify raw database crawler uses the correct role
	rawDbCrawlerRole := terraform.Output(t, terraformOptions, "glue_raw_database_crawler_role")
	assert.Equal(t, glueRoleArn, rawDbCrawlerRole, "Raw database crawler should use Glue role")

	// Verify raw CSV crawler uses the correct role
	rawCsvCrawlerRole := terraform.Output(t, terraformOptions, "glue_raw_csv_crawler_role")
	assert.Equal(t, glueRoleArn, rawCsvCrawlerRole, "Raw CSV crawler should use Glue role")
}


// TestS3 tests that a new S3 bucket is created
func TestS3(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name": "autocorp-test-s3",
			"environment":  "dev",
			"enable_dms":   false,
			"enable_datasync": false,
		},
		Targets: []string{"module.s3"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	bucketName := terraform.Output(t, terraformOptions, "data_lake_bucket_id")
	assert.Contains(t, bucketName, "autocorp-test-s3", "Bucket name should contain project name")
}

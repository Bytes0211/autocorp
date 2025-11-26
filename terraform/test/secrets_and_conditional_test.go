package test

import (
	"strings"
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

// TestSecretsManagerConfiguration tests that the Secrets Manager secret is created
// with the correct naming convention and description
func TestSecretsManagerConfiguration(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":   "autocorp-test-secrets",
			"environment":    "dev",
			"enable_dms":     false,
			"enable_datasync": false,
		},
		Targets: []string{"module.secrets"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify secret ARN exists
	secretArn := terraform.Output(t, terraformOptions, "postgres_password_secret_arn")
	assert.NotEmpty(t, secretArn, "Secret ARN should not be empty")

	// Verify secret name follows naming convention: project_name/environment/postgres/password
	secretName := terraform.Output(t, terraformOptions, "postgres_password_secret_name")
	expectedSecretName := "autocorp-test-secrets/dev/postgres/password"
	assert.Equal(t, expectedSecretName, secretName, "Secret name should follow naming convention")

	// Verify secret description mentions PostgreSQL and DMS
	secretDescription := terraform.Output(t, terraformOptions, "postgres_password_secret_description")
	assert.Contains(t, strings.ToLower(secretDescription), "postgresql", "Description should mention PostgreSQL")
	assert.Contains(t, strings.ToLower(secretDescription), "dms", "Description should mention DMS")
}

// TestSecretsManagerProdEnvironment tests secret naming for production environment
func TestSecretsManagerProdEnvironment(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":   "autocorp-prod",
			"environment":    "prod",
			"enable_dms":     false,
			"enable_datasync": false,
		},
		Targets: []string{"module.secrets"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Verify secret name for prod environment
	secretName := terraform.Output(t, terraformOptions, "postgres_password_secret_name")
	expectedSecretName := "autocorp-prod/prod/postgres/password"
	assert.Equal(t, expectedSecretName, secretName, "Secret name should use prod environment")
}

// TestDMSModuleConditionalCreation tests that the DMS module is conditionally
// created based on the enable_dms variable
func TestDMSModuleConditionalCreation(t *testing.T) {
	t.Parallel()

	// Test Case 1: DMS disabled (default)
	t.Run("DMSDisabled", func(t *testing.T) {
		terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
			TerraformDir: "../",
			Vars: map[string]interface{}{
				"project_name":   "autocorp-test-dms-off",
				"environment":    "dev",
				"enable_dms":     false,
				"enable_datasync": false,
			},
		})

		defer terraform.Destroy(t, terraformOptions)
		terraform.InitAndApply(t, terraformOptions)

		// Get all outputs
		outputs := terraform.OutputAll(t, terraformOptions)

		// Verify DMS-specific outputs don't exist
		_, dmsReplicationInstanceExists := outputs["dms_replication_instance_arn"]
		assert.False(t, dmsReplicationInstanceExists, "DMS replication instance should not be created when disabled")

		_, dmsEndpointExists := outputs["dms_source_endpoint_arn"]
		assert.False(t, dmsEndpointExists, "DMS source endpoint should not be created when disabled")
	})

	// Test Case 2: DMS enabled
	// Note: This test would require PostgreSQL connectivity, so we verify the count logic
	t.Run("DMSEnabled", func(t *testing.T) {
		terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
			TerraformDir: "../",
			Vars: map[string]interface{}{
				"project_name":     "autocorp-test-dms-on",
				"environment":      "dev",
				"enable_dms":       true,
				"postgres_host":    "test.postgres.local",
				"postgres_database": "autocorp",
				"postgres_username": "testuser",
				"enable_datasync":   false,
			},
			// Only plan, don't apply since we don't have real PostgreSQL
			PlanFilePath: "/tmp/tfplan",
		})

		// Run plan to verify module would be created
		exitCode := terraform.InitAndPlanWithExitCode(t, terraformOptions)
		
		// Exit code 2 means changes would be applied (module would be created)
		// Exit code 0 means no changes
		// Exit code 1 means error
		assert.NotEqual(t, 1, exitCode, "Plan should not fail")
		
		if exitCode == 2 {
			// Parse plan to verify DMS module is included
			planOutput := terraform.Plan(t, terraformOptions)
			assert.Contains(t, planOutput, "module.dms[0]", "DMS module should be included in plan when enabled")
		}
	})
}

// TestDataSyncModuleConditionalCreation tests that the DataSync module is conditionally
// created based on the enable_datasync variable
func TestDataSyncModuleConditionalCreation(t *testing.T) {
	t.Parallel()

	// Test Case 1: DataSync disabled (default)
	t.Run("DataSyncDisabled", func(t *testing.T) {
		terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
			TerraformDir: "../",
			Vars: map[string]interface{}{
				"project_name":   "autocorp-test-ds-off",
				"environment":    "dev",
				"enable_dms":     false,
				"enable_datasync": false,
			},
		})

		defer terraform.Destroy(t, terraformOptions)
		terraform.InitAndApply(t, terraformOptions)

		// Get all outputs
		outputs := terraform.OutputAll(t, terraformOptions)

		// Verify DataSync-specific outputs don't exist
		_, datasyncTaskExists := outputs["datasync_task_arn"]
		assert.False(t, datasyncTaskExists, "DataSync task should not be created when disabled")

		_, datasyncLocationExists := outputs["datasync_s3_location_arn"]
		assert.False(t, datasyncLocationExists, "DataSync S3 location should not be created when disabled")
	})

	// Test Case 2: DataSync enabled
	t.Run("DataSyncEnabled", func(t *testing.T) {
		terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
			TerraformDir: "../",
			Vars: map[string]interface{}{
				"project_name":   "autocorp-test-ds-on",
				"environment":    "dev",
				"enable_dms":     false,
				"enable_datasync": true,
				"datasync_agent_arns": []string{
					"arn:aws:datasync:us-east-1:123456789012:agent/agent-12345678",
				},
			},
			// Only plan, don't apply since we don't have real agents
			PlanFilePath: "/tmp/tfplan-datasync",
		})

		// Run plan to verify module would be created
		exitCode := terraform.InitAndPlanWithExitCode(t, terraformOptions)
		
		assert.NotEqual(t, 1, exitCode, "Plan should not fail")
		
		if exitCode == 2 {
			// Parse plan to verify DataSync module is included
			planOutput := terraform.Plan(t, terraformOptions)
			assert.Contains(t, planOutput, "module.datasync[0]", "DataSync module should be included in plan when enabled")
		}
	})
}

// TestConditionalModulesIndependence tests that DMS and DataSync can be enabled independently
func TestConditionalModulesIndependence(t *testing.T) {
	t.Parallel()

	// Test: Both modules disabled
	t.Run("BothDisabled", func(t *testing.T) {
		terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
			TerraformDir: "../",
			Vars: map[string]interface{}{
				"project_name":   "autocorp-test-both-off",
				"environment":    "dev",
				"enable_dms":     false,
				"enable_datasync": false,
			},
			Targets: []string{"module.s3", "module.iam", "module.secrets", "module.glue"},
		})

		defer terraform.Destroy(t, terraformOptions)
		terraform.InitAndApply(t, terraformOptions)

		// Verify base modules are created
		bucketId := terraform.Output(t, terraformOptions, "data_lake_bucket_id")
		assert.NotEmpty(t, bucketId, "S3 bucket should be created")

		glueRoleArn := terraform.Output(t, terraformOptions, "glue_role_arn")
		assert.NotEmpty(t, glueRoleArn, "Glue role should be created")

		secretArn := terraform.Output(t, terraformOptions, "postgres_password_secret_arn")
		assert.NotEmpty(t, secretArn, "Secret should be created")
	})
}

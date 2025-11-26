package test

import (
	"encoding/json"
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// AssumeRolePolicy represents the structure of an IAM assume role policy
type AssumeRolePolicy struct {
	Version   string `json:"Version"`
	Statement []struct {
		Action    string `json:"Action"`
		Effect    string `json:"Effect"`
		Principal struct {
			Service string `json:"Service"`
		} `json:"Principal"`
	} `json:"Statement"`
}

// PolicyDocument represents the structure of an IAM policy document
type PolicyDocument struct {
	Version   string `json:"Version"`
	Statement []struct {
		Effect   string   `json:"Effect"`
		Action   []string `json:"Action"`
		Resource interface{} `json:"Resource"`
	} `json:"Statement"`
}

// TestGlueRoleConfiguration tests that the Glue IAM role is created with correct
// assume role policy and inline policies
func TestGlueRoleConfiguration(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":   "autocorp-test-glue",
			"environment":    "dev",
			"enable_dms":     false,
			"enable_datasync": false,
		},
		Targets: []string{"module.s3", "module.iam"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Get Glue role ARN
	glueRoleArn := terraform.Output(t, terraformOptions, "glue_role_arn")
	assert.NotEmpty(t, glueRoleArn, "Glue role ARN should not be empty")

	// Verify role name follows naming convention
	glueRoleName := terraform.Output(t, terraformOptions, "glue_role_name")
	assert.Equal(t, "autocorp-test-glue-glue-role-dev", glueRoleName, "Glue role name should follow naming convention")

	// Verify assume role policy allows Glue service
	assumeRolePolicyJSON := terraform.Output(t, terraformOptions, "glue_assume_role_policy")
	var assumeRolePolicy AssumeRolePolicy
	err := json.Unmarshal([]byte(assumeRolePolicyJSON), &assumeRolePolicy)
	require.NoError(t, err, "Should parse assume role policy JSON")

	assert.Equal(t, "2012-10-17", assumeRolePolicy.Version)
	assert.Len(t, assumeRolePolicy.Statement, 1)
	assert.Equal(t, "sts:AssumeRole", assumeRolePolicy.Statement[0].Action)
	assert.Equal(t, "Allow", assumeRolePolicy.Statement[0].Effect)
	assert.Equal(t, "glue.amazonaws.com", assumeRolePolicy.Statement[0].Principal.Service)

	// Verify inline policy grants S3 and Glue permissions
	inlinePolicyJSON := terraform.Output(t, terraformOptions, "glue_inline_policy")
	var inlinePolicy PolicyDocument
	err = json.Unmarshal([]byte(inlinePolicyJSON), &inlinePolicy)
	require.NoError(t, err, "Should parse inline policy JSON")

	assert.Equal(t, "2012-10-17", inlinePolicy.Version)
	assert.GreaterOrEqual(t, len(inlinePolicy.Statement), 2, "Should have at least 2 statements")

	// Verify S3 permissions
	s3Statement := inlinePolicy.Statement[0]
	assert.Equal(t, "Allow", s3Statement.Effect)
	assert.Contains(t, s3Statement.Action, "s3:GetObject")
	assert.Contains(t, s3Statement.Action, "s3:PutObject")
	assert.Contains(t, s3Statement.Action, "s3:ListBucket")

	// Verify Glue and CloudWatch Logs permissions
	glueStatement := inlinePolicy.Statement[1]
	assert.Equal(t, "Allow", glueStatement.Effect)
	assert.Contains(t, glueStatement.Action, "glue:*")
	assert.Contains(t, glueStatement.Action, "logs:CreateLogGroup")
}

// TestDMSRoleConfiguration tests that the DMS IAM role is created with correct
// assume role policy and inline policies
func TestDMSRoleConfiguration(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":   "autocorp-test-dms",
			"environment":    "dev",
			"enable_dms":     false,
			"enable_datasync": false,
		},
		Targets: []string{"module.s3", "module.iam"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Get DMS role ARN
	dmsRoleArn := terraform.Output(t, terraformOptions, "dms_role_arn")
	assert.NotEmpty(t, dmsRoleArn, "DMS role ARN should not be empty")

	// Verify role name follows naming convention
	dmsRoleName := terraform.Output(t, terraformOptions, "dms_role_name")
	assert.Equal(t, "autocorp-test-dms-dms-role-dev", dmsRoleName, "DMS role name should follow naming convention")

	// Verify assume role policy allows DMS service
	assumeRolePolicyJSON := terraform.Output(t, terraformOptions, "dms_assume_role_policy")
	var assumeRolePolicy AssumeRolePolicy
	err := json.Unmarshal([]byte(assumeRolePolicyJSON), &assumeRolePolicy)
	require.NoError(t, err, "Should parse assume role policy JSON")

	assert.Equal(t, "2012-10-17", assumeRolePolicy.Version)
	assert.Equal(t, "dms.amazonaws.com", assumeRolePolicy.Statement[0].Principal.Service)

	// Verify inline policy grants S3 write access to raw/database/ only
	inlinePolicyJSON := terraform.Output(t, terraformOptions, "dms_inline_policy")
	var inlinePolicy PolicyDocument
	err = json.Unmarshal([]byte(inlinePolicyJSON), &inlinePolicy)
	require.NoError(t, err, "Should parse inline policy JSON")

	// Check that S3 write permissions are scoped to raw/database/
	s3Statement := inlinePolicy.Statement[0]
	assert.Equal(t, "Allow", s3Statement.Effect)
	assert.Contains(t, s3Statement.Action, "s3:PutObject")
	
	// Verify resource is scoped correctly
	resources := s3Statement.Resource.([]interface{})
	resourceStr := resources[0].(string)
	assert.Contains(t, resourceStr, "/raw/database/*", "DMS should only write to raw/database/")
}

// TestDataSyncRoleConfiguration tests that the DataSync IAM role is created with correct
// assume role policy and inline policies
func TestDataSyncRoleConfiguration(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"project_name":   "autocorp-test-ds",
			"environment":    "dev",
			"enable_dms":     false,
			"enable_datasync": false,
		},
		Targets: []string{"module.s3", "module.iam"},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	// Get DataSync role ARN
	datasyncRoleArn := terraform.Output(t, terraformOptions, "datasync_role_arn")
	assert.NotEmpty(t, datasyncRoleArn, "DataSync role ARN should not be empty")

	// Verify role name follows naming convention
	datasyncRoleName := terraform.Output(t, terraformOptions, "datasync_role_name")
	assert.Equal(t, "autocorp-test-ds-datasync-role-dev", datasyncRoleName, "DataSync role name should follow naming convention")

	// Verify assume role policy allows DataSync service
	assumeRolePolicyJSON := terraform.Output(t, terraformOptions, "datasync_assume_role_policy")
	var assumeRolePolicy AssumeRolePolicy
	err := json.Unmarshal([]byte(assumeRolePolicyJSON), &assumeRolePolicy)
	require.NoError(t, err, "Should parse assume role policy JSON")

	assert.Equal(t, "2012-10-17", assumeRolePolicy.Version)
	assert.Equal(t, "datasync.amazonaws.com", assumeRolePolicy.Statement[0].Principal.Service)

	// Verify inline policy grants S3 access to raw/csv/ only
	inlinePolicyJSON := terraform.Output(t, terraformOptions, "datasync_inline_policy")
	var inlinePolicy PolicyDocument
	err = json.Unmarshal([]byte(inlinePolicyJSON), &inlinePolicy)
	require.NoError(t, err, "Should parse inline policy JSON")

	// Check that S3 permissions are scoped to raw/csv/
	s3Statement := inlinePolicy.Statement[0]
	assert.Equal(t, "Allow", s3Statement.Effect)
	assert.Contains(t, s3Statement.Action, "s3:PutObject")
	assert.Contains(t, s3Statement.Action, "s3:GetObject")
	
	// Verify resources are scoped correctly
	resources := s3Statement.Resource.([]interface{})
	resourceStr := resources[0].(string)
	assert.Contains(t, resourceStr, "/raw/csv/*", "DataSync should only access raw/csv/")
}

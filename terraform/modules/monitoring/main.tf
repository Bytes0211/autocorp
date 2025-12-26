# CloudWatch Dashboard for AutoCorp Data Lake
resource "aws_cloudwatch_dashboard" "autocorp" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      # Glue Job Metrics
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Glue", "glue.driver.aggregate.numSucceededTasks", {"stat": "Sum"}],
            [".", "glue.driver.aggregate.numFailedTasks", {"stat": "Sum"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Glue Job Task Success/Failure"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Glue", "glue.driver.ExecutorAllocationManager.executors.numberAllExecutors", {"stat": "Average"}],
            [".", "glue.driver.ExecutorAllocationManager.executors.numberMaxNeededExecutors", {"stat": "Average"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Glue Executor Allocation"
          period  = 300
        }
      },
      # Athena Query Metrics
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Athena", "EngineExecutionTime", {"stat": "Average"}],
            [".", "DataScannedInBytes", {"stat": "Sum", "yAxis": "right"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Athena Query Performance"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Athena", "TotalExecutionTime", {"stat": "Average"}],
            [".", "QueryPlanningTime", {"stat": "Average"}],
            [".", "QueryQueueTime", {"stat": "Average"}],
            [".", "ServiceProcessingTime", {"stat": "Average"}]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.aws_region
          title   = "Athena Query Time Breakdown"
          period  = 300
        }
      },
      # S3 Metrics
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/S3", "BucketSizeBytes", {"stat": "Average"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "S3 Data Lake Size"
          period  = 86400
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/S3", "NumberOfObjects", {"stat": "Average"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "S3 Object Count"
          period  = 86400
        }
      },
      # Cost Tracking (estimated)
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", {"stat": "Maximum"}]
          ]
          view    = "singleValue"
          stacked = false
          region  = "us-east-1"
          title   = "Estimated Daily Costs"
          period  = 86400
        }
      },
      # Log Insights Query Results
      {
        type = "log"
        properties = {
          query   = "SOURCE '/aws-glue/jobs/error' | fields @timestamp, @message | sort @timestamp desc | limit 20"
          region  = var.aws_region
          title   = "Recent Glue Job Errors"
        }
      }
    ]
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "glue_job_failures" {
  alarm_name          = "${var.project_name}-glue-job-failures-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "glue.driver.aggregate.numFailedTasks"
  namespace           = "AWS/Glue"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors Glue job task failures"
  treat_missing_data  = "notBreaching"

  alarm_actions = var.sns_topic_arn != "" ? [var.sns_topic_arn] : []
}

resource "aws_cloudwatch_metric_alarm" "athena_query_failures" {
  alarm_name          = "${var.project_name}-athena-failures-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "QueryFailed"
  namespace           = "AWS/Athena"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors Athena query failures"
  treat_missing_data  = "notBreaching"

  alarm_actions = var.sns_topic_arn != "" ? [var.sns_topic_arn] : []
}

resource "aws_cloudwatch_metric_alarm" "high_cost_alert" {
  count = var.enable_cost_alerts ? 1 : 0

  alarm_name          = "${var.project_name}-high-cost-alert-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"
  statistic           = "Maximum"
  threshold           = var.daily_cost_threshold
  alarm_description   = "Alert when daily AWS costs exceed threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    Currency = "USD"
  }

  alarm_actions = var.sns_topic_arn != "" ? [var.sns_topic_arn] : []
}

# SNS Topic for Alerts (optional)
resource "aws_sns_topic" "alerts" {
  count = var.create_sns_topic ? 1 : 0

  name              = "${var.project_name}-alerts-${var.environment}"
  display_name      = "AutoCorp Alert Notifications"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "email" {
  count = var.create_sns_topic && var.alert_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Log Groups for Glue Jobs
resource "aws_cloudwatch_log_group" "glue_jobs" {
  for_each = toset(var.glue_job_names)

  name              = "/aws-glue/jobs/${each.key}"
  retention_in_days = var.log_retention_days

  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Log Groups for Glue Crawlers
resource "aws_cloudwatch_log_group" "glue_crawlers" {
  for_each = toset(var.glue_crawler_names)

  name              = "/aws-glue/crawlers/${each.key}"
  retention_in_days = var.log_retention_days

  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

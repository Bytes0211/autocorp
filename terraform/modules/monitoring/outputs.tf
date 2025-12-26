output "dashboard_arn" {
  description = "ARN of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.autocorp.dashboard_arn
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.autocorp.dashboard_name
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = var.create_sns_topic ? aws_sns_topic.alerts[0].arn : var.sns_topic_arn
}

output "glue_job_failure_alarm_arn" {
  description = "ARN of Glue job failure alarm"
  value       = aws_cloudwatch_metric_alarm.glue_job_failures.arn
}

output "athena_failure_alarm_arn" {
  description = "ARN of Athena query failure alarm"
  value       = aws_cloudwatch_metric_alarm.athena_query_failures.arn
}

output "high_cost_alarm_arn" {
  description = "ARN of high cost alert alarm"
  value       = var.enable_cost_alerts ? aws_cloudwatch_metric_alarm.high_cost_alert[0].arn : null
}

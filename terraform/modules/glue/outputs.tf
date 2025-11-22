# Glue Module Outputs

output "database_name" {
  description = "Name of the Glue Data Catalog database"
  value       = aws_glue_catalog_database.autocorp.name
}

output "crawler_names" {
  description = "Names of the Glue crawlers"
  value = concat(
    var.enable_crawlers ? [aws_glue_crawler.raw_database[0].name] : [],
    var.enable_crawlers ? [aws_glue_crawler.raw_csv[0].name] : []
  )
}

# Run all checks in sequence
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === S3 Buckets ==="
aws s3 ls | grep autocorp
echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] === IAM Roles ==="
aws iam list-roles --query 'Roles[?contains(RoleName, `autocorp`)].RoleName' --output table
echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] === Secrets Manager ==="
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `autocorp`)].Name' --output table
echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] === Glue Databases ==="
aws glue get-databases --query 'DatabaseList[?contains(Name, `autocorp`)].Name' --output table
echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] === Glue Crawlers ==="
aws glue list-crawlers --query 'CrawlerNames[?contains(@, `autocorp`)]' --output table
echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] === Glue Jobs ==="
aws glue list-jobs --query 'JobNames[?contains(@, `autocorp`)]' --output table
echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] === DMS Replication Instances (if deployed) ==="
aws dms describe-replication-instances --query 'ReplicationInstances[?contains(ReplicationInstanceIdentifier, `autocorp`)].ReplicationInstanceIdentifier' --output table 2>/dev/null || echo "[$(date '+%Y-%m-%d %H:%M:%S')] DMS not deployed or not accessible"

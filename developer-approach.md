# Developer's Approach Document

**Project Name:** AutoCorp Data Lake Pipeline
**Author:** S Cotton
**Date:** 2025-11-21
**Status:** In Review

---

## 1. Overview

Create an AWS-based data pipeline that ingests data from a PostgreSQL database and CSV files into a data lake, enabling analytics and querying through open table formats (Apache Hudi and Delta Lake).

### Goals
- **Primary:** Establish a scalable data lake architecture for AutoCorp's operational data
- **Secondary:** Enable real-time analytics and historical data queries using open table formats
- **Tertiary:** Implement automated data quality checks and transformation pipelines

### Success Criteria
- All PostgreSQL tables successfully replicated to S3 data lake via AWS DMS
- CSV files (sales orders, customers) automatically synced to S3 via AWS DataSync
- Data cataloged and queryable via AWS Athena
- Apache Hudi and Delta Lake tables created for time-travel and ACID transactions
- End-to-end pipeline running with <15 minute data freshness

---

## 2. Background & Context

### Current State
- **PostgreSQL Database:** `autocorp` database on-premises with 7 tables:
  - `auto_parts` (400 rows) - Parts inventory
  - `customers` (1,149 rows) - Customer information
  - `service` (110 rows) - Service catalog
  - `service_parts` (1,074 rows) - Service-to-parts mapping
  - `sales_order` (1,000 rows) - Order headers
  - `sales_order_parts` (2,135 rows) - Parts line items
  - `sales_order_services` (644 rows) - Service line items

- **CSV Files:** 
  - `customers.csv` (1.2M records) - Full customer dataset
  - Sales order CSV files (generated periodically)

### Requirements
- **R1:** Migrate all database tables to AWS data lake without data loss
- **R2:** Establish continuous replication for database changes (CDC)
- **R3:** Automate CSV file ingestion with scheduling flexibility
- **R4:** Implement data quality checks and validation
- **R5:** Support both batch and incremental data loading
- **R6:** Enable SQL queries on data lake via Athena
- **R7:** Implement open table formats for advanced analytics

### Constraints
- **Technical:** Must maintain ACID properties for critical tables
- **Business:** Minimal disruption to operational database
- **Cost:** AWS resources must be optimized for cost-effectiveness
- **Security:** Data at rest and in transit must be encrypted
- **Compliance:** Maintain data lineage and audit trails

---

## 3. Proposed Solution

### High-Level Approach

Implement a multi-layer data architecture:
1. **Ingestion Layer:** AWS DMS (database) + AWS DataSync (CSV files)
2. **Raw Storage Layer:** S3 buckets organized by source and date
3. **Processing Layer:** AWS Glue for ETL and data quality
4. **Curated Layer:** Apache Hudi and Delta Lake tables
5. **Query Layer:** AWS Athena for SQL analytics

### Architecture Diagram

```
┌─────────────────────┐
│ Source Systems      │
├─────────────────────┤
│ PostgreSQL DB       │──────► AWS DMS ──────────┐
│ - 7 tables          │      (CDC Replication)    │
│ - 5,668 total rows  │                           │
└─────────────────────┘                           │
                                                   │
┌─────────────────────┐                           ▼
│ CSV Files           │              ┌────────────────────────┐
├─────────────────────┤              │   S3 Data Lake         │
│ customers.csv       │──► DataSync ─►   (Raw Zone)           │
│ sales_orders.csv    │              │ - /raw/database/       │
└─────────────────────┘              │ - /raw/csv/            │
                                     └────────────────────────┘
                                                   │
                                                   ▼
                                     ┌────────────────────────┐
                                     │   AWS Glue             │
                                     │ - Crawler (catalog)    │
                                     │ - ETL Jobs (clean)     │
                                     │ - Data Quality Rules   │
                                     └────────────────────────┘
                                                   │
                                                   ▼
                                     ┌────────────────────────┐
                                     │   S3 Data Lake         │
                                     │   (Curated Zone)       │
                                     │ - Apache Hudi tables   │
                                     │ - Delta Lake tables    │
                                     └────────────────────────┘
                                                   │
                                                   ▼
                                     ┌────────────────────────┐
                                     │   AWS Athena           │
                                     │   (Query Engine)       │
                                     └────────────────────────┘
```

### Key Components

1. **AWS DMS (Database Migration Service)**
   - Purpose: Replicate PostgreSQL tables to S3
   - Responsibilities:
     - Full load of existing data
     - Continuous data capture (CDC) for ongoing changes
     - Schema conversion and mapping
     - Write to S3 in Parquet format
   - Configuration:
     - Source: PostgreSQL endpoint
     - Target: S3 bucket (`s3://autocorp-datalake/raw/database/`)
     - Replication instance: `dms.t3.medium`

2. **AWS DataSync**
   - Purpose: Transfer CSV files from on-premises to S3
   - Responsibilities:
     - Scheduled or triggered file transfers
     - Data validation and integrity checks
     - Bandwidth optimization
   - Configuration:
     - Source: On-premises file location
     - Destination: S3 bucket (`s3://autocorp-datalake/raw/csv/`)
     - Schedule: Hourly or event-driven

3. **AWS Glue Crawler**
   - Purpose: Auto-discover and catalog data schemas
   - Responsibilities:
     - Scan S3 raw zone
     - Infer schemas
     - Update AWS Glue Data Catalog
     - Create/update table definitions
   - Schedule: After DMS/DataSync completion

4. **AWS Glue ETL Jobs**
   - Purpose: Data cleaning, transformation, and quality checks
   - Responsibilities:
     - Deduplicate records
     - Validate data types and constraints
     - Standardize formats
     - Apply business rules
     - Write to curated zone
   - Language: PySpark

5. **Apache Hudi Tables**
   - Purpose: Manage incremental data with ACID properties
   - Responsibilities:
     - Upsert operations (merge on key)
     - Time-travel queries
     - Record-level updates
   - Use cases: `sales_order`, `customers` (high update frequency)
   - Table type: Copy-on-Write (COW)

6. **Delta Lake Tables**
   - Purpose: ACID transactions with schema evolution
   - Responsibilities:
     - Maintain transaction log
     - Enable schema evolution
     - Support DML operations
   - Use cases: `auto_parts`, `service` (reference data)
   - Features: Time-travel, VACUUM for cleanup

7. **AWS Athena**
   - Purpose: Serverless SQL query engine
   - Responsibilities:
     - Query data directly on S3
     - Support for Hudi and Delta Lake
     - Integration with BI tools
   - Configuration: Glue Data Catalog as metastore

### Data Flow

**Database Replication Flow:**
```
PostgreSQL → DMS Replication → S3 Raw (Parquet) 
  → Glue Crawler → Glue ETL → S3 Curated (Hudi/Delta) 
  → Athena Query
```

**CSV Ingestion Flow:**
```
On-Premises CSV → DataSync → S3 Raw (CSV) 
  → Glue Crawler → Glue ETL → S3 Curated (Hudi/Delta) 
  → Athena Query
```

### Design Decisions

- **Decision:** Use both Apache Hudi and Delta Lake
  - **Rationale:** 
    - Hudi excels at upsert workloads (sales orders)
    - Delta Lake better for batch analytics (reference data)
    - Evaluate both for future standardization
  - **Trade-offs:** Additional operational complexity

- **Decision:** Parquet format for raw zone
  - **Rationale:** Columnar format, excellent compression, AWS native support
  - **Trade-offs:** Not human-readable (vs CSV/JSON)

- **Decision:** Three-zone architecture (raw/processed/curated)
  - **Rationale:** Data lineage, reprocessing capability, different SLAs
  - **Trade-offs:** Increased storage costs

- **Decision:** AWS DMS over custom CDC solution
  - **Rationale:** Managed service, proven reliability, minimal code
  - **Trade-offs:** AWS vendor lock-in, DMS-specific limitations

---

## 4. Implementation Details

### Technology Stack
- **AWS DMS:** Database migration and CDC - Managed service, no code required
- **AWS DataSync:** File transfer - Automated, optimized bandwidth usage
- **AWS S3:** Data lake storage - Scalable, durable, cost-effective
- **AWS Glue:** ETL and data catalog - Serverless, PySpark-based
- **Apache Hudi 0.14+:** Transactional data lake - Upsert support, time-travel
- **Delta Lake 3.0+:** ACID transactions - Schema evolution, DML operations
- **AWS Athena:** Query engine - Serverless SQL, pay-per-query
- **AWS IAM:** Access control - Fine-grained permissions
- **AWS CloudWatch:** Monitoring - Logs, metrics, alarms

### S3 Bucket Structure

```
s3://autocorp-datalake/
├── raw/
│   ├── database/
│   │   ├── auto_parts/
│   │   │   └── year=2024/month=11/day=21/
│   │   ├── customers/
│   │   ├── service/
│   │   ├── service_parts/
│   │   ├── sales_order/
│   │   ├── sales_order_parts/
│   │   └── sales_order_services/
│   └── csv/
│       ├── customers/
│       │   └── customers-20241121.csv
│       └── sales_orders/
│           └── sales_orders-20241121.csv
├── curated/
│   ├── hudi/
│   │   ├── sales_order/
│   │   └── customers/
│   └── delta/
│       ├── auto_parts/
│       ├── service/
│       └── service_parts/
└── logs/
    ├── dms/
    ├── glue/
    └── datasync/
```

### Key Implementation Areas

#### DMS Replication Setup
1. Create replication instance in same VPC as PostgreSQL
2. Configure source endpoint (PostgreSQL)
3. Configure target endpoint (S3)
4. Create replication tasks:
   - Full load task for initial migration
   - CDC task for ongoing changes
5. Table mappings with selection rules
6. Enable CloudWatch logging

**DMS Task Configuration:**
```json
{
  "TargetMetadata": {
    "SupportLobs": true,
    "FullLobMode": false,
    "LobMaxSize": 32
  },
  "FullLoadSettings": {
    "TargetTablePrepMode": "DROP_AND_CREATE",
    "MaxFullLoadSubTasks": 8
  },
  "ChangeProcessingTuning": {
    "BatchApplyTimeoutMin": 1,
    "BatchApplyTimeoutMax": 30,
    "BatchSplitSize": 0,
    "MinTransactionSize": 1000,
    "CommitTimeout": 1
  }
}
```

#### AWS Glue ETL Job for Hudi

**PySpark Script:**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Initialize Spark with Hudi
spark = SparkSession.builder \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()

# Read from raw zone
df = spark.read.parquet("s3://autocorp-datalake/raw/database/sales_order/")

# Data quality checks
df_clean = df \
    .dropDuplicates(["order_id"]) \
    .filter(col("total_amount") > 0) \
    .withColumn("etl_timestamp", current_timestamp())

# Write to Hudi
hudi_options = {
    'hoodie.table.name': 'sales_order',
    'hoodie.datasource.write.recordkey.field': 'order_id',
    'hoodie.datasource.write.partitionpath.field': 'order_date',
    'hoodie.datasource.write.table.name': 'sales_order',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'updated_at',
    'hoodie.upsert.shuffle.parallelism': 20,
    'hoodie.insert.shuffle.parallelism': 20
}

df_clean.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://autocorp-datalake/curated/hudi/sales_order/")
```

#### AWS Glue ETL Job for Delta Lake

**PySpark Script:**
```python
from delta import *
from pyspark.sql import SparkSession

# Initialize Spark with Delta Lake
spark = SparkSession.builder \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Read from raw zone
df = spark.read.parquet("s3://autocorp-datalake/raw/database/auto_parts/")

# Write to Delta Lake
df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .save("s3://autocorp-datalake/curated/delta/auto_parts/")

# Create Delta table in Glue Catalog
spark.sql("""
    CREATE TABLE IF NOT EXISTS autocorp_catalog.auto_parts
    USING DELTA
    LOCATION 's3://autocorp-datalake/curated/delta/auto_parts/'
""")
```

### Migration Strategy

**Phase 1: Infrastructure Setup (Week 1)**
- Create AWS accounts and IAM roles
- Set up VPC and security groups
- Create S3 buckets with lifecycle policies
- Deploy DMS replication instance

**Phase 2: Initial Data Load (Week 2)**
- Configure DMS source/target endpoints
- Run full load tasks for all tables
- Validate data integrity (row counts, checksums)
- Set up DataSync tasks for CSV files

**Phase 3: CDC & Automation (Week 3)**
- Enable CDC on DMS tasks
- Deploy Glue crawlers (scheduled)
- Deploy Glue ETL jobs (triggered by crawler)
- Test end-to-end pipeline

**Phase 4: Open Table Formats (Week 4)**
- Create Hudi tables for transactional data
- Create Delta Lake tables for reference data
- Configure Athena to query both formats
- Performance tuning and optimization

---

## 5. Alternatives Considered

### Alternative 1: Custom Python CDC with Debezium
- **Description:** Use Debezium for CDC + custom Python scripts for S3 upload
- **Pros:** 
  - Full control over CDC logic
  - Can customize transformation in-flight
  - No DMS costs
- **Cons:** 
  - Requires Kafka cluster management
  - More code to maintain
  - Need to handle failure scenarios
- **Why not chosen:** Higher operational overhead, DMS is proven and managed

### Alternative 2: Single Table Format (Hudi or Delta only)
- **Description:** Standardize on one table format instead of both
- **Pros:** 
  - Simpler architecture
  - Single set of tools/skills
  - Easier to troubleshoot
- **Cons:** 
  - Miss benefits of specialized formats
  - May not be optimal for all use cases
- **Why not chosen:** Want to evaluate both in production workloads before standardizing

### Alternative 3: AWS Lake Formation for Governance
- **Description:** Use Lake Formation for fine-grained access control
- **Pros:** 
  - Column-level security
  - Centralized governance
  - Tag-based access control
- **Cons:** 
  - Additional complexity
  - Learning curve
  - Not needed for current scale
- **Why not chosen:** IAM policies sufficient for Phase 1, can add later

---

## 6. Testing Strategy

### Test Approach
1. **Unit Tests:** Glue ETL job logic (PySpark)
2. **Integration Tests:** End-to-end pipeline with test data
3. **Data Quality Tests:** Row counts, schema validation, constraint checks
4. **Performance Tests:** Load testing with varying data volumes
5. **Failover Tests:** Simulate DMS/Glue failures

### Key Test Scenarios
- **Full Load Test:** Migrate all 5,668 rows from PostgreSQL
- **CDC Test:** Insert/update/delete operations replicated within 5 minutes
- **CSV Ingestion:** 1.2M customer records loaded and cataloged
- **Query Performance:** Athena queries return <30 seconds for aggregations
- **Hudi Upsert:** Update existing sales_order, verify latest version
- **Delta Time-Travel:** Query auto_parts as of yesterday
- **Schema Evolution:** Add column to service table, ETL adapts

### Edge Cases
- **Duplicate Records:** ETL deduplicates based on primary key
- **Null Values:** Handle missing data gracefully (not fail job)
- **Large Objects:** Sales orders with 50+ line items
- **Schema Changes:** Table columns added/removed in source
- **Network Interruptions:** DMS resumes from checkpoint
- **Concurrent Updates:** Multiple updates to same record

---

## 7. Non-Functional Considerations

### Performance
- **DMS Replication:** <5 minute lag for CDC (target: 2-3 minutes)
- **Glue ETL:** Process 1M rows in <10 minutes
- **Athena Queries:** Simple aggregations <10 seconds, complex <30 seconds
- **Data Freshness:** End-to-end <15 minutes (source to queryable)
- **Optimization Strategies:**
  - Partition by date for time-series data
  - Use Parquet compression (SNAPPY)
  - Glue job parallelism tuning
  - Athena query result caching
  - Hudi/Delta compaction schedules

### Security
- **Encryption at Rest:** S3 SSE-S3 (can upgrade to KMS)
- **Encryption in Transit:** TLS 1.2+ for all connections
- **Access Control:** IAM roles with least privilege
  - DMS role: Read from PostgreSQL, write to S3
  - Glue role: Read/write S3, update catalog
  - Athena role: Read S3 curated zone only
- **Network:** VPC endpoints for AWS services (no internet)
- **Auditing:** CloudTrail for all API calls
- **Database Credentials:** Secrets Manager (not hardcoded)

### Scalability
- **Current Scale:** 5,668 rows, <1GB total
- **Expected Growth:** 10K new sales orders/month, 50K rows/month
- **Scalability Limits:**
  - DMS: Millions of rows, TB scale
  - S3: Virtually unlimited
  - Glue: 100 DPUs (can scale to 1000+)
  - Athena: Scans up to PB scale
- **Scaling Strategy:**
  - Horizontal: Add more Glue workers
  - Partitioning: Increase granularity as data grows
  - Compaction: Regular Hudi/Delta compaction

### Observability
- **Logging:**
  - DMS logs to CloudWatch (replication tasks)
  - Glue logs to CloudWatch (job runs, errors)
  - DataSync logs to CloudWatch (transfer status)
- **Metrics:**
  - DMS: CDC latency, rows replicated
  - Glue: Job duration, rows processed
  - Athena: Query count, scanned bytes
  - S3: Storage size, request counts
- **Alarms:**
  - DMS replication lag >10 minutes
  - Glue job failures
  - S3 bucket size >threshold
  - Athena query failures
- **Dashboard:** CloudWatch custom dashboard with key metrics

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| DMS replication lag during peak hours | High | Medium | Right-size replication instance, enable Multi-AZ, monitor lag |
| Data quality issues in source | Medium | Medium | Implement Glue Data Quality rules, alerts on violations |
| S3 cost overruns | Medium | Low | Lifecycle policies (move to Glacier after 90 days), budget alerts |
| Schema drift breaks ETL | High | Medium | Schema evolution in Delta, version ETL code, test in dev |
| Network connectivity issues | High | Low | VPC peering, redundant connections, DMS auto-resume |
| Glue job failures | Medium | Medium | Retry logic, error handling, CloudWatch alarms |
| Hudi/Delta learning curve | Low | High | Training, documentation, POC before production |
| AWS service limits | Low | Low | Request limit increases proactively, monitor usage |

---

## 9. Timeline & Milestones

### Phase 1: Infrastructure & Setup (Week 1)
- **Duration:** 5 days
- **Deliverables:**
  - AWS account setup, IAM roles created
  - S3 buckets with proper structure
  - VPC, security groups, endpoints configured
  - DMS replication instance deployed
  - DataSync agent installed on-premises

### Phase 2: Initial Data Migration (Week 2)
- **Duration:** 5 days
- **Deliverables:**
  - DMS endpoints configured
  - Full load tasks completed (all 7 tables)
  - Data validation (row counts match)
  - CSV files synced to S3
  - Glue crawler initial run

### Phase 3: CDC & ETL Pipeline (Week 3)
- **Duration:** 5 days
- **Deliverables:**
  - CDC enabled on all DMS tasks
  - Glue ETL jobs deployed
  - Data quality rules configured
  - End-to-end testing complete
  - Documentation updated

### Phase 4: Open Table Formats (Week 4)
- **Duration:** 5 days
- **Deliverables:**
  - Hudi tables for sales_order, customers
  - Delta Lake tables for reference data
  - Athena queries validated
  - Performance benchmarks documented
  - Handoff to operations team

---

## 10. Open Questions

- [ ] Should we implement Lake Formation for governance in Phase 1 or defer?
- [ ] What is the retention policy for raw zone data? (30/60/90 days?)
- [ ] Do we need cross-region replication for disaster recovery?
- [ ] Should DataSync run hourly or triggered by file arrival?
- [ ] What BI tools will query Athena? (affects query optimization)
- [ ] Do we need real-time dashboards or batch is sufficient?
- [ ] Should we use Glue DataBrew for data profiling?
- [ ] What's the backup strategy for Hudi/Delta tables?

---

## 11. References

### AWS Documentation
- [AWS DMS Best Practices](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html)
- [AWS DataSync User Guide](https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html)
- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)

### Open Table Formats
- [Apache Hudi Documentation](https://hudi.apache.org/docs/overview)
- [Delta Lake Documentation](https://docs.delta.io/latest/index.html)
- [Hudi vs Delta Lake Comparison](https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-transparent-tpc-ds-lakehouse-performance-benchmarks)

### Internal Documentation
- `DATABASE_STATUS.md` - Current database schema and statistics
- `SALES_SYSTEM_USAGE.md` - SQL query examples
- `README.md` - Project overview

### Related Tools
- `generate_sales_orders.py` - Sales order generator for testing
- `upload_customers.py` - Customer data loader

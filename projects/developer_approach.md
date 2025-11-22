# Developer's Approach Document

**Project Name:** AutoCorp Data Lake Pipeline
**Author:** S Cotton
**Date:** 2025-11-21
**Status:** In Review

---

## 1. Overview

The AutoCorp project is a comprehensive cloud-based data architecture that extends beyond a traditional database system. It encompasses a complete data lifecycle from operational database to data lake, data warehouse, and analytics platform. The finished project implements a modern AWS data lakehouse architecture enabling scalable analytics, real-time querying, and business intelligence capabilities across the organization's sales and service data.

**Infrastructure as Code Implementation:** The entire AWS infrastructure is deployed using Terraform with 95% automation coverage. See Section 9 for complete IaC implementation details, including 6 reusable modules, multi-environment support, and deployment procedures.

### Goals

- **Primary:** Build an end-to-end cloud data platform integrating data lake, data warehouse, and analytics capabilities
- **Secondary:** Enable enterprise-wide data accessibility through SQL querying (AWS Athena) and BI tools
- **Tertiary:** Implement open table formats (Apache Hudi) for ACID transactions and time-travel capabilities
- **Quaternary:** Establish automated data pipelines with quality checks and governance
- **Infrastructure:** Deploy complete AWS infrastructure as code using Terraform (95% automation)

### Success Criteria

- **Data Ingestion:** PostgreSQL database replicated to S3 data lake via AWS DMS with CDC enabled
- **File Integration:** Large CSV files (customers, sales orders) automatically synced via AWS DataSync
- **Data Catalog:** All data sources cataloged in AWS Glue Data Catalog with automated schema discovery
- **Open Table Formats:** Apache Hudi tables operational for transactional data with upsert capabilities
- **Query Layer:** AWS Athena configured as primary query engine with sub-30 second query performance
- **Data Freshness:** End-to-end pipeline delivering <15 minute data latency from source to analytics layer
- **Scalability:** Architecture handles considerable CSV file sizes (multi-GB) efficiently
- **Infrastructure Automation:** 95% of infrastructure deployed via Terraform with version control and multi-environment support

## 2. Background & Context

### Current State

The AutoCorp project begins with an operational PostgreSQL database and large-scale CSV exports, but evolves into a comprehensive data platform:

- **PostgreSQL Database (Source):** `autocorp` database on-premises with 7 tables:
  - `auto_parts` (400 rows) - Parts inventory
  - `customers` (1,149 rows) - Customer information
  - `service` (110 rows) - Service catalog
  - `service_parts` (1,074 rows) - Service-to-parts mapping
  - `sales_order` (1,000 rows) - Order headers
  - `sales_order_parts` (2,135 rows) - Parts line items
  - `sales_order_services` (644 rows) - Service line items

- **CSV Files (Large-Scale Data):**
  - `customers.csv` (1.2M records, considerable file size) - Full customer dataset
  - Sales order CSV files (multi-GB exports generated periodically)
  - Historical data archives requiring efficient transfer mechanisms

### Project Scope: Beyond Database Management

This is **not just a database system**. The complete AutoCorp data platform delivers:

1. **AWS Data Lake:** Centralized S3-based repository for all raw and processed data
2. **Data Warehouse Capabilities:** Curated, analytics-ready datasets in open table formats
3. **Query Engine:** AWS Athena providing SQL interface to data lake without moving data
4. **Data Catalog:** AWS Glue metadata management for all data assets
5. **Automated Pipelines:** Continuous data extraction, transformation, and loading

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

Implement a modern data lakehouse architecture with distinct functional layers:

1. **Ingestion Layer:**
   - **AWS DMS:** Continuous database extraction with Change Data Capture (CDC)
   - **AWS DataSync:** Efficient transfer of considerable-size CSV files from on-premises to cloud

2. **Raw Storage Layer (Data Lake):**
   - **AWS S3:** Scalable, durable object storage organized by source and date partitions
   - Landing zone for all raw data before transformation

3. **Catalog & Metadata Layer:**
   - **AWS Glue Data Catalog:** Centralized metadata repository
   - **AWS Glue Crawlers:** Automated schema discovery and catalog updates

4. **Processing Layer (ETL):**
   - **AWS Glue ETL Jobs:** PySpark-based data cleaning, transformation, and quality validation
   - Data deduplication, standardization, and business rule application

5. **Curated Layer (Data Warehouse):**
   - **Apache Hudi Tables:** Open table format providing ACID transactions, upserts, and time-travel
   - Analytics-ready datasets optimized for query performance

6. **Query & Analytics Layer:**
   - **AWS Athena:** Serverless SQL query engine directly on S3 data
   - No data movement required, pay-per-query model
   - Compatible with standard BI tools (Tableau, PowerBI, etc.)

### Architecture Diagram

```txt
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

```txt
PostgreSQL → DMS Replication → S3 Raw (Parquet) 
  → Glue Crawler → Glue ETL → S3 Curated (Hudi/Delta) 
  → Athena Query
```

**CSV Ingestion Flow:**

```txt
On-Premises CSV → DataSync → S3 Raw (CSV) 
  → Glue Crawler → Glue ETL → S3 Curated (Hudi/Delta) 
  → Athena Query
```

### Design Decisions

- **Decision:** Standardize on Apache Hudi for open table format
  - **Rationale:**
    - Hudi excels at upsert workloads (sales orders, customer updates)
    - Strong AWS integration and Athena support
    - Mature CDC and incremental processing capabilities
    - Meets project needs for ACID transactions and time-travel
  - **Trade-offs:** Single format simplifies operations and reduces complexity

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

**Data Ingestion & Extraction:**

- **AWS DMS:** Database migration and continuous data capture (CDC) - Managed service for PostgreSQL replication
- **AWS DataSync:** High-performance file transfer - Handles considerable CSV file sizes with optimization

**Data Lake & Storage:**

- **AWS S3:** Object storage foundation - Scalable, durable (99.999999999% durability), cost-effective
- **S3 Lifecycle Policies:** Automated data tiering for cost optimization

**Data Catalog & Metadata:**

- **AWS Glue Data Catalog:** Centralized metadata repository - Apache Hive Metastore compatible
- **AWS Glue Crawlers:** Automated schema discovery - Keeps catalog synchronized with data

**ETL & Processing:**

- **AWS Glue ETL:** Serverless PySpark execution - Auto-scaling, managed infrastructure
- **Apache Hudi 0.14+:** Open table format - ACID transactions, upserts, time-travel, incremental processing

**Query & Analytics:**

- **AWS Athena:** Serverless SQL query engine - Pay-per-query, direct S3 querying, Hudi-native support
- **Presto/Trino Engine:** Powers Athena with distributed query execution

**Security & Governance:**

- **AWS IAM:** Identity and access management - Fine-grained permissions, service roles
- **AWS Secrets Manager:** Secure credential storage - Database passwords, API keys
- **S3 Encryption:** SSE-S3/SSE-KMS for data at rest

**Observability & Operations:**

- **AWS CloudWatch:** Centralized logging and metrics - Dashboards, alarms, log insights
- **CloudTrail:** Audit logging for all AWS API calls

### S3 Bucket Structure

```txt
s3://autocorp-datalake/
├── raw/
│   ├── database/                    # DMS destination - database CDC data
│   │   ├── auto_parts/
│   │   │   └── year=2024/month=11/day=21/
│   │   ├── customers/
│   │   ├── service/
│   │   ├── service_parts/
│   │   ├── sales_order/
│   │   ├── sales_order_parts/
│   │   └── sales_order_services/
│   └── csv/                         # DataSync destination - large CSV files
│       ├── customers/
│       │   └── customers-20241121.csv  # Considerable size (multi-GB)
│       └── sales_orders/
│           └── sales_orders-20241121.csv
├── curated/                         # Analytics-ready data warehouse layer
│   └── hudi/                        # Apache Hudi open table format
│       ├── sales_order/             # Transactional data with upserts
│       ├── customers/               # Customer master data
│       ├── auto_parts/              # Parts inventory
│       ├── service/                 # Service catalog
│       ├── service_parts/           # Service-parts relationships
│       ├── sales_order_parts/       # Sales line items
│       └── sales_order_services/    # Service line items
└── logs/                            # Pipeline execution logs
    ├── dms/                         # DMS task logs
    ├── glue/                        # ETL job execution logs
    └── datasync/                    # DataSync transfer logs
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

#### AWS Glue ETL Job for Reference Data (Batch)

**PySpark Script for auto_parts (lower update frequency):**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Initialize Spark with Hudi
spark = SparkSession.builder \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()

# Read from raw zone
df = spark.read.parquet("s3://autocorp-datalake/raw/database/auto_parts/")

# Data quality and transformations
df_clean = df \
    .dropDuplicates(["part_id"]) \
    .filter(col("price") > 0) \
    .withColumn("etl_timestamp", current_timestamp())

# Write to Hudi (merge-on-read for batch updates)
hudi_options = {
    'hoodie.table.name': 'auto_parts',
    'hoodie.datasource.write.recordkey.field': 'part_id',
    'hoodie.datasource.write.precombine.field': 'updated_at',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.write.hive_style_partitioning': 'true'
}

df_clean.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://autocorp-datalake/curated/hudi/auto_parts/")
```

### Migration Strategy

#### Phase 1: Infrastructure Setup (Week 1)

- Create AWS accounts and IAM roles
- Set up VPC and security groups
- Create S3 buckets with lifecycle policies
- Deploy DMS replication instance

#### Phase 2: Initial Data Load (Week 2)

- Configure DMS source/target endpoints
- Run full load tasks for all tables
- Validate data integrity (row counts, checksums)
- Set up DataSync tasks for CSV files

#### Phase 3: CDC & Automation (Week 3)

- Enable CDC on DMS tasks
- Deploy Glue crawlers (scheduled)
- Deploy Glue ETL jobs (triggered by crawler)
- Test end-to-end pipeline

#### Phase 4: Open Table Formats & Query Layer (Week 4)

- Create Hudi tables for all data entities (transactional and reference)
- Configure Athena workgroups and query result locations
- Implement query performance optimizations (partitioning, compression)
- Validate time-travel and incremental query capabilities
- Test Athena integration with BI tools

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

### Alternative 2: Delta Lake Instead of Hudi

- **Description:** Use Delta Lake as the open table format
- **Pros:** 
  - Strong Databricks ecosystem integration
  - Rich DML support (DELETE, UPDATE, MERGE)
  - Schema evolution capabilities
- **Cons:** 
  - Less mature AWS Athena integration compared to Hudi
  - Weaker CDC and streaming ingestion support
  - Additional connector requirements for Athena
- **Why not chosen:** Hudi provides better AWS-native integration and stronger CDC capabilities for this use case

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

## 6. Testing Strategy

### Test Approach

1. **Unit Tests:** Glue ETL job logic (PySpark)
2. **Integration Tests:** End-to-end pipeline with test data
3. **Data Quality Tests:** Row counts, schema validation, constraint checks
4. **Performance Tests:** Load testing with varying data volumes
5. **Failover Tests:** Simulate DMS/Glue failures

### Key Test Scenarios

- **Full Load Test:** Migrate all 1607343 rows from PostgreSQL
- **CDC Test:** Insert/update/delete operations replicated within 5 minutes
- **CSV Ingestion:** 1.2M customer records loaded and cataloged
- **Query Performance:** Athena queries return <30 seconds for aggregations
- **Hudi Upsert:** Update existing sales_order, verify latest version retrieved
- **Hudi Time-Travel:** Query auto_parts as of yesterday using Hudi's timestamp-based queries
- **Schema Evolution:** Add column to service table, Hudi and Glue ETL adapt automatically
- **Incremental Queries:** Use Hudi's incremental query feature for changed records only

### Edge Cases

- **Duplicate Records:** ETL deduplicates based on primary key
- **Null Values:** Handle missing data gracefully (not fail job)
- **Large Objects:** Sales orders with 50+ line items
- **Schema Changes:** Table columns added/removed in source
- **Network Interruptions:** DMS resumes from checkpoint
- **Concurrent Updates:** Multiple updates to same record


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
  - Horizontal: Add more Glue workers (DPUs)
  - Partitioning: Increase granularity as data grows (daily → hourly)
  - Compaction: Regular Hudi compaction to optimize small files
  - DataSync: Parallel file transfers for large CSV batches

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

## 9. Infrastructure as Code (IaC) Implementation

### Approach: Terraform for AWS Infrastructure

**Decision:** Implement all AWS infrastructure using Terraform for version control, repeatability, and disaster recovery capabilities.

**Feasibility:** 95% - All four core services (S3, Glue, DMS, DataSync) have excellent Terraform support with only minor manual steps required.

### IaC Project Structure

```
terraform/
├── main.tf                    # Root module orchestration
├── variables.tf               # Input variables
├── outputs.tf                 # Infrastructure outputs
├── terraform.tfvars           # Default variable values
├── backend.tf                 # Remote state (S3 + DynamoDB)
├── versions.tf                # Provider version constraints
│
├── modules/
│   ├── s3/                    # Data lake storage [100% IaC]
│   ├── iam/                   # Service roles [100% IaC]
│   ├── secrets/               # Secrets Manager [100% IaC]
│   ├── glue/                  # Data catalog & ETL [100% IaC]
│   ├── dms/                   # Database replication [90% IaC]
│   └── datasync/              # File transfers [80% IaC]
│
└── environments/
    ├── dev.tfvars             # Development config
    ├── staging.tfvars         # Staging config
    └── prod.tfvars            # Production config
```

### IaC Benefits

1. **Version Control:** All infrastructure changes tracked in Git
2. **Repeatability:** Deploy to dev/staging/prod with consistency
3. **Disaster Recovery:** Recreate entire infrastructure from code
4. **Drift Detection:** `terraform plan` shows configuration drift
5. **Documentation:** Infrastructure is self-documenting code
6. **Collaboration:** Team can review changes via pull requests
7. **Cost Control:** Preview cost changes before deployment
8. **Multi-Environment:** Easy environment cloning and testing

### Manual Steps (Cannot Be IaC'd)

1. **Terraform State Bootstrap:** Create S3 bucket and DynamoDB table for remote state (one-time)
2. **PostgreSQL Configuration:** Enable logical replication on source database
3. **DataSync Agent:** Deploy and activate agent on-premises VM
4. **Secrets:** Manually set PostgreSQL password in Secrets Manager (security)

### Implementation Phases (IaC-Based)

**Phase 1: Foundation (Week 1) - 100% IaC**

- S3 buckets with folder structure
- IAM roles (Glue, DMS, DataSync)
- Secrets Manager placeholder
- Terraform state backend

**Phase 2: Data Catalog (Week 2) - 100% IaC**

- Glue Data Catalog
- Glue Crawlers (scheduled)
- Glue ETL jobs with PySpark scripts
- Glue triggers and workflows

**Phase 3: Database Replication (Week 2-3) - 90% IaC**
- DMS replication instance
- DMS endpoints (PostgreSQL, S3)
- DMS replication tasks with CDC
- Manual: Network connectivity testing

**Phase 4: File Transfers (Week 3) - 80% IaC**
- DataSync locations (on-premises, S3)
- DataSync tasks with schedules
- Manual: Agent deployment and activation

### State Management

**Remote State Configuration:**
```hcl
terraform {
  backend "s3" {
    bucket         = "autocorp-terraform-state"
    key            = "datalake/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "autocorp-terraform-locks"
  }
}
```

**Benefits:**
- Shared state for team collaboration
- State locking prevents concurrent modifications
- Versioning enables rollback
- Encrypted at rest

### Security Considerations

**Secrets Management:**
- Store PostgreSQL password in AWS Secrets Manager (IaC-managed)
- Never commit secrets to Git (.gitignore for *.tfvars with secrets)
- Use IAM roles for service authentication
- Rotate credentials via Secrets Manager

**IAM Least Privilege:**
- Each service role has minimum required permissions
- S3 access scoped to specific paths (raw/, curated/, logs/)
- CloudTrail audit logging for all AWS API calls

**Encryption:**
- S3: SSE-S3 encryption at rest
- DMS: TLS 1.2+ for PostgreSQL connections
- Glue: Job bookmarks encrypted
- Secrets Manager: KMS encryption

### Deployment Commands

```bash
# Initialize Terraform
cd terraform
terraform init

# Preview changes
terraform plan

# Deploy to dev
terraform apply

# Deploy to production
terraform apply -var-file="environments/prod.tfvars"

# Destroy (cleanup)
terraform destroy
```

### Cost Estimation (IaC Deployed)

Monthly AWS costs (dev environment):
- S3 storage: $5-10 (1-2 TB with lifecycle)
- Glue Crawlers: $5-10 (daily runs)
- Glue ETL: $15-30 (20 DPU-hours/day)
- DMS: $50-80 (t3.medium continuous)
- DataSync: $10-20 (100 GB/day)
- Secrets Manager: $1
- **Total: $86-151/month**

Production costs will be higher due to:
- Increased DMS instance size (t3.large or larger)
- More frequent ETL jobs
- Higher data transfer volumes
- Multi-AZ deployments for HA

**References:**
- See `IAC_FEASIBILITY_ASSESSMENT.md` for detailed IaC analysis
- See `terraform/README.md` for deployment instructions

---

## 10. Timeline & Milestones

### Phase 1: Infrastructure & Setup (Week 1)
- **Duration:** 5 days
- **Deliverables:**
  - Terraform project structure created
  - S3 module deployed (data lake buckets)
  - IAM module deployed (service roles)
  - Secrets Manager configured
  - Terraform state backend initialized
  - DMS replication instance deployed (IaC)

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

### Phase 4: Open Table Formats & Analytics (Week 4)
- **Duration:** 5 days
- **Deliverables:**
  - Hudi tables operational for all entities
  - Athena workgroups configured with query result buckets
  - Query performance validated (<30s for aggregations)
  - Time-travel and incremental query examples documented
  - BI tool integration tested (if applicable)
  - Complete documentation and handoff to operations team

---

## 11. Open Questions

- [ ] Should we implement Lake Formation for governance in Phase 1 or defer?
- [ ] What is the retention policy for raw zone data? (30/60/90 days?)
- [ ] Do we need cross-region replication for disaster recovery?
- [ ] Should DataSync run hourly, daily, or triggered by file arrival?
- [ ] What BI tools will query Athena? (Tableau, PowerBI, QuickSight?) - affects optimization
- [ ] Do we need real-time dashboards or is batch analytics sufficient?
- [ ] Should we use Glue DataBrew for data profiling and quality rules?
- [ ] What's the backup strategy for Hudi tables and Glue Catalog?
- [ ] Should we partition Hudi tables by date, region, or other dimensions?
- [ ] How do we handle very large CSV files (>10GB)? Split before DataSync?

---

## 12. References

### AWS Documentation
- [AWS DMS Best Practices](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html)
- [AWS DataSync User Guide](https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html)
- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)

### Open Table Formats & Data Lakehouse
- [Apache Hudi Documentation](https://hudi.apache.org/docs/overview)
- [Using Apache Hudi with AWS Glue](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-hudi-on-aws/welcome.html)
- [Querying Hudi Tables with Athena](https://docs.aws.amazon.com/athena/latest/ug/querying-hudi.html)
- [Data Lakehouse Architecture Patterns](https://aws.amazon.com/blogs/big-data/build-a-lake-house-architecture-on-aws/)

### Internal Documentation
- `DATABASE_STATUS.md` - Current database schema and statistics
- `SALES_SYSTEM_USAGE.md` - SQL query examples
- `README.md` - Project overview

### Related Tools
- `generate_sales_orders.py` - Sales order generator for testing
- `upload_customers.py` - Customer data loader

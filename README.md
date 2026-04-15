# AutoCorp Cloud Data Lake Pipeline

## Why This Project Matters

AutoCorp simulates a real enterprise data platform with CDC ingestion, lakehouse storage, serverless ETL, analytics, and AI‑powered search. It demonstrates my ability to architect and deliver production‑grade cloud systems end‑to‑end.

## Key Skills Demonstrated

- AWS data engineering (S3, Glue, DMS, DataSync, Athena)
- Lakehouse architecture with Apache Hudi
- IaC with Terraform (multi‑env, modules, 119 resources)
- Serverless backend (Lambda + API Gateway)
- RAG with Bedrock Nova Pro + OpenSearch
- Data quality engineering
- PySpark ETL
- Next.js  frontend

## Project Overview

AutoCorp is a comprehensive **cloud-native data platform** that extends beyond traditional database management to deliver a complete data lifecycle solution. The project showcases modern data engineering practices with AWS services, Infrastructure as Code, and open table formats.

### What This Project Delivers

**Core Data Platform:**

- **AWS Data Lake:** S3-based lakehouse with raw, curated, and logs zones
- **Real-time CDC Replication:** PostgreSQL → AWS DMS → S3 (Parquet) with <5 minute lag
- **Serverless ETL:** AWS Glue jobs transforming raw data to Apache Hudi tables
- **Query Engine:** AWS Athena for SQL analytics directly on data lake
- **AI Chatbox (Phase 5):** Amazon Bedrock Nova Pro with RAG for customer support & analytics
- **Infrastructure as Code:** Complete Terraform implementation (95% automated)

**Source System (PostgreSQL):**

- **Auto parts inventory** (400 parts)
- **Service catalog** (110 services across 11 categories)
- **Customer management** (1,149 customers)
- **Sales orders** (397,146 orders with 1.6M total rows)
- **Service-parts relationships** (1,074 mappings)

**CSV Data Files:**

- **Historical sales data** (792K unique orders, 1.86M rows with intentional duplicates)
- **Combined dataset** (1.19M total unique orders for testing)
- **Data Quality Testing:** Duplicates demonstrate ETL deduplication using Hudi upserts

### Key Technical Achievements

- ✅ **<15 minute end-to-end data latency** from source to queryable
- ✅ **CDC with <5 minute lag** using AWS DMS (IaC ready)
- ✅ **Apache Hudi tables** with ACID transactions and time-travel queries
- ✅ **Terraform IaC** with 95% automation (8 modules, 119 AWS resources)
- ✅ **Multi-environment support** (dev/staging/prod) via IaC
- ✅ **Cost-optimized** S3 lifecycle policies (raw → Glacier after 90 days)
- ✅ **AI chatbox with RAG** Amazon Bedrock Nova Pro + Knowledge Base (1,584 docs)
- ✅ **Serverless backend** Lambda + API Gateway with 3-second response times

## Architecture Overview

### Complete Data Lakehouse + AI Architecture

```mermaid
graph TB
    subgraph Sources["Source Systems"]
        PG["PostgreSQL DB<br/>- 7 tables<br/>- 1.6M rows"]
        CSV["CSV Files<br/>- customers.csv<br/>- sales_orders.csv"]
    end
    
    subgraph Ingestion["Data Ingestion Layer"]
        DMS["AWS DMS<br/>(CDC Replication)<br/>[IaC Ready]"]
        DS["AWS DataSync<br/>[Documented]"]
    end
    
    subgraph RawZone["S3 Data Lake - Raw Zone"]
        S3Raw["S3 Bucket<br/>- /raw/database/<br/>- /raw/csv/<br/>- /knowledge-base/"]
    end
    
    subgraph Transform["ETL & Processing Layer"]
        Glue["AWS Glue<br/>- 3 Crawlers<br/>- 11 ETL Jobs (PySpark)<br/>- Data Quality Rules"]
    end
    
    subgraph CuratedZone["S3 Data Lake - Curated Zone"]
        S3Curated["S3 Bucket<br/>- 10 Apache Hudi Tables<br/>- ACID Transactions<br/>- Time Travel"]
    end
    
    subgraph Analytics["Analytics & Query Layer"]
        Athena["AWS Athena<br/>(Query Engine)<br/>- 5 Named Queries<br/>- Time-travel Queries"]
    end
    
    subgraph AI["AI/ML Layer"]
        Bedrock["Amazon Bedrock<br/>- Knowledge Base (1,584 docs)<br/>- Nova Pro (LLM)<br/>- Titan Embeddings G1"]
        AOSS["OpenSearch Serverless<br/>(Vector Store)"]
    end
    
    subgraph Backend["Serverless Backend"]
        Lambda["AWS Lambda<br/>- Chat Function<br/>- Analytics Function<br/>(Python 3.12)"]
        APIGW["API Gateway (REST)<br/>- /chat endpoint<br/>- /analytics endpoint<br/>- CORS + API Keys"]
    end
    
    subgraph Frontend["Frontend Layer"]
        NextJS["Next.js Frontend<br/>(S3 Static Hosting)<br/>- React + TypeScript<br/>- Live at S3 Website"]
    end
    
    %% Data Flow
    PG -->|CDC Stream| DMS
    CSV -->|File Transfer| DS
    DMS -->|Parquet Files| S3Raw
    DS -->|CSV Upload| S3Raw
    S3Raw -->|Schema Discovery| Glue
    Glue -->|Transform & Load| S3Curated
    S3Curated -->|Query| Athena
    S3Raw -->|Documents| Bedrock
    Bedrock <-->|Vector Search| AOSS
    Athena -->|SQL Analytics| Lambda
    Bedrock -->|RAG Response| Lambda
    Lambda -->|REST API| APIGW
    APIGW -->|HTTPS| NextJS
    
    %% Styling
    classDef sourceStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef ingestionStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef transformStyle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef analyticsStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef aiStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef backendStyle fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef frontendStyle fill:#e8eaf6,stroke:#1a237e,stroke-width:2px
    
    class PG,CSV sourceStyle
    class DMS,DS ingestionStyle
    class S3Raw,S3Curated storageStyle
    class Glue transformStyle
    class Athena analyticsStyle
    class Bedrock,AOSS aiStyle
    class Lambda,APIGW backendStyle
    class NextJS frontendStyle
```

### AWS Services Stack

| Service | Purpose | Configuration | Status |
|---------|---------|---------------|--------|
| **Data Lake Layer (Phases 1-2)** |
| **AWS S3** | Data lake storage | Raw/curated/logs/knowledge-base zones | ✅ Operational |
| **AWS Glue** | Data catalog & ETL | 11 PySpark jobs, 3 crawlers, Hudi transformations | ✅ Operational |
| **AWS IAM** | Service roles | Least-privilege roles for all services | ✅ Operational |
| **AWS Secrets Manager** | Credentials storage | PostgreSQL credentials | ✅ Operational |
| **CDC Replication Layer (Phase 3)** |
| **AWS DMS** | PostgreSQL CDC replication | dms.t3.medium, <5min lag | 📝 IaC Ready |
| **AWS DataSync** | Large CSV file transfers | Hourly sync, multi-GB files | 📖 Documented |
| **Analytics Layer (Phase 4)** |
| **AWS Athena** | Serverless SQL queries | 5 named queries, sub-30s performance | ✅ Operational |
| **AWS CloudWatch** | Monitoring & alerts | Dashboard + 3 alarms (Glue, Athena, Cost) | ✅ Operational |
| **AI/ML Layer (Phase 5 - Complete)** |
| **Amazon Bedrock** | AI foundation models | Nova Pro (LLM) + Titan Embeddings + Knowledge Base (1,584 docs) | ✅ Operational |
| **OpenSearch Serverless** | Vector database for RAG | 2GB collection with semantic search | ✅ Operational |
| **AWS Lambda** | Serverless API functions | Chat + Analytics functions (Python 3.12) | ✅ Operational |
| **API Gateway** | REST API endpoints | /chat + /analytics with CORS + API keys | ✅ Operational |
| **S3 Static Website** | Frontend hosting | Next.js 16.1.1 + React + TypeScript (static export) | ✅ Operational |
| **Open Source** |
| **Apache Hudi** | Open table format | ACID, upserts, time-travel | ✅ Operational |
| **Terraform** | Infrastructure as Code | 8 modules, 119 AWS resources, 95% automated | ✅ Operational |

## Database Structure (Source System)

**Database Name:** `autocorp`  
**Total Tables:** 7  
**Total Data Rows:** 1,605,804

### Tables

- `auto_parts` - Parts inventory (400 rows)
- `customers` - Customer information (1,149 rows)
- `service` - Service catalog (110 rows)
- `service_parts` - Service-to-parts mapping (1,074 rows)
- `sales_order` - Order headers (397,146 rows)
- `sales_order_parts` - Parts line items (853,591 rows)
- `sales_order_services` - Service line items (355,067 rows)

### CSV Data Files (For DataSync Testing)

- `sales_orders.csv` - Historical orders (791,532 unique, 1,864,774 total rows)
  - **Data Quality Feature:** Contains intentional duplicates for ETL testing
  - **Demonstrates:** Hudi upsert deduplication using invoice_number as record key
- `sales_order_parts.csv` - Historical parts line items (4,877,041 rows)
- `sales_order_services.csv` - Historical service line items (529,488 rows)
- **Total CSV data:** 7,271,303 rows across 3 files
- **Unique orders in CSV:** 791,532 (duplicates simulate real-world data issues)
- **Combined dataset:** 1,188,678 total unique orders (PostgreSQL + CSV)

## Infrastructure as Code (Terraform)

### Terraform Project Structure

```txt
terraform/
├── main.tf                    # Root module orchestration
├── variables.tf               # Input variables
├── outputs.tf                 # Infrastructure outputs
├── terraform.tfvars           # Default values
├── backend.tf                 # Remote state (S3)
├── versions.tf                # Provider versions
│
├── modules/
│   ├── s3/                    # Data lake [✅ OPERATIONAL]
│   ├── iam/                   # Service roles [✅ OPERATIONAL]
│   ├── secrets/               # Secrets Manager [✅ OPERATIONAL]
│   ├── glue/                  # ETL & catalog [✅ OPERATIONAL]
│   ├── dms/                   # CDC replication [📝 IaC READY]
│   ├── athena/                # Query workgroup [✅ OPERATIONAL]
│   ├── bedrock/               # AI/ML Knowledge Base [✅ OPERATIONAL]
│   └── lambda-chat/           # Chat API functions [✅ OPERATIONAL]
│
└── environments/
    ├── dev.tfvars             # Development
    ├── staging.tfvars         # Staging
    └── prod.tfvars            # Production
```

**Deployment:**

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**IaC Coverage:** 95% automated (only manual: DataSync agent, PostgreSQL config)

## Project Files

### Source Data (CSV)

- `auto-parts.csv` - Auto parts inventory source data
- `auto-service.csv` - Service catalog source data
- `service-parts.csv` - Service-to-parts mapping source data
- `customers.csv` - Customer data source (1.2M records, 1,149 loaded)

### Database Scripts (SQL)

- `create_auto_parts_table.sql` - Creates auto_parts table
- `create_service_table.sql` - Creates service table
- `create_sales_system.sql` - Creates complete sales system (orders, line items, views)

### Python Scripts

- `upload_customers.py` - Randomly selects and uploads 1,150 customers from CSV
  - **Usage:** `.venv/bin/python upload_customers.py`
  - **Features:** Random sampling, duplicate handling, progress reporting

- `generate_sales_orders_csv.py` - Generates sales orders with data quality testing features
  - **Usage:** `python generate_sales_orders_csv.py`
  - **Features:** 791,532 orders with configurable data quality issues for ETL testing
  - **Output:** 3 CSV files + validation manifest JSON
  - **Purpose:** Test AWS DataSync → Glue Crawler → Data Catalog pipeline robustness

### Documentation
- `README.md` - This file (project overview)
- `developer-approach.md` - **850-line comprehensive technical architecture**
- `IAC_FEASIBILITY_ASSESSMENT.md` - **588-line IaC analysis**
- `PROJECT_GANTT_CHART.md` - **307-line project timeline & status**
- `DEPLOYMENT_SUMMARY.md` - **AI chatbox deployment summary with live URL**
- `frontend/autocorp-chatbox/IMPLEMENTATION.md` - **Frontend implementation guide**
- `terraform/README.md` - **297-line deployment guide**
- `DATABASE_STATUS.md` - Database schema and statistics
- `SALES_SYSTEM_USAGE.md` - SQL query examples (10+ queries)
- `DATA_QUALITY_TESTING.md` - **326-line comprehensive ETL testing guide**
- `DATA_QUALITY_QUICK_REFERENCE.md` - **136-line quick reference for DQ testing**
- `docs/parts_selection_and_correction.md` - **253-line guide on RAG parts retrieval and correction process**

### Configuration
- `requirements.txt` - Python dependencies
- `Makefile` - Project automation commands
- `.gitignore` - Git exclusions
- `.venv/` - Python virtual environment

## Setup Instructions

### Prerequisites
- PostgreSQL installed and running
- Python 3.12+ with venv support
- Database `autocorp` created

### Initial Setup

1. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/pip install psycopg2-binary
   ```

2. **Create database tables:**
   ```bash
   # Auto parts table
   psql -U scotton -d autocorp -f create_auto_parts_table.sql
   
   # Service table
   psql -U scotton -d autocorp -f create_service_table.sql
   
   # Sales system (orders, line items, views)
   psql -U scotton -d autocorp -f create_sales_system.sql
   ```

3. **Load data:**
   ```bash
   # Load customers (randomly selects 1,150 from 1.2M)
   .venv/bin/python upload_customers.py
   
   # Load services and service-parts data
   # (SQL INSERT scripts would be generated from CSVs)
   ```

## Key Features

### Cloud Data Platform Capabilities

**Data Engineering:**
- ✅ **CDC Replication:** Real-time database changes captured via AWS DMS
- ✅ **Open Table Formats:** Apache Hudi tables with ACID transactions
- ✅ **Serverless ETL:** AWS Glue PySpark jobs for data transformation
- ✅ **Time-Travel Queries:** Query data as of any historical timestamp
- ✅ **Incremental Processing:** Hudi supports efficient upserts and deletes
- ✅ **Data Quality:** Glue Data Quality rules with automated validation

**Infrastructure Automation:**
- ✅ **Infrastructure as Code:** Complete Terraform implementation
- ✅ **Multi-Environment:** Dev/staging/prod configuration management
- ✅ **State Management:** Remote state with S3 + DynamoDB locking
- ✅ **Cost Optimization:** S3 lifecycle policies, right-sized instances
- ✅ **Security:** Secrets Manager, IAM least privilege, encryption

**Analytics & Querying:**
- ✅ **Analytics Layer:** Denormalized wide tables for 80%+ faster BI queries
- ✅ **Serverless SQL:** AWS Athena queries on data lake (no data movement)
- ✅ **Sub-30s Performance:** Optimized partitioning and compression
- ✅ **BI Integration:** Compatible with Tableau, PowerBI, QuickSight
- ✅ **Dual-Layer Architecture:** Normalized (operational) + denormalized (analytics) tables

**Data Quality Testing:**
- ✓ **Duplicate Record Handling:** CSV files contain intentional duplicates for Hudi upsert testing
- ✓ **Missing Value Injection:** Test ETL null handling (6 configurable parameters)
- ✓ **Invalid Data Testing:** Malformed dates, formatted numbers, whitespace issues
- ✓ **Edge Case Testing:** Negative amounts, out-of-range dates, zero quantities
- ✓ **Validation Manifest:** JSON ground truth for expected vs. actual data quality issues
- ✓ **Pipeline Robustness:** Comprehensive testing for DataSync → Glue → Catalog workflows
- ✓ **Deduplication Strategy:** invoice_number as Hudi record key for automatic duplicate removal

### Database System Features

**Unified Sales System:**
- Single invoice can contain parts and/or services
- Three order types: `Parts`, `Service`, `Mixed`
- Automatic tracking of service-parts relationships
- Foreign key integrity with customers

### Service-Parts Mapping
- Each service linked to required parts via `service_parts` table
- Supports multiple parts per service
- Quantity tracking for each part-service relationship

### Customer Management
- Random sampling from large dataset (1.2M → 1,149)
- Email uniqueness enforced
- Geographic distribution across 59 states

## AWS Data Pipeline Operations

### Deploy Infrastructure (IaC)
```bash
# Initialize Terraform
cd terraform
terraform init

# Preview changes
terraform plan

# Deploy to dev environment
terraform apply

# Deploy to production
terraform apply -var-file="environments/prod.tfvars"
```

### Query Data Lake with Athena
```sql
-- Query Hudi table with time-travel
SELECT order_id, customer_id, total_amount, order_date
FROM "autocorp_dev"."sales_order"
WHERE order_date >= CURRENT_DATE - INTERVAL '7' DAY;

-- Incremental query (changes since last run)
SELECT *
FROM "autocorp_dev"."sales_order"
WHERE _hoodie_commit_time > '20250101000000';
```

### Monitor DMS Replication
```bash
# Check CDC lag
aws dms describe-replication-tasks \
  --filters Name=replication-task-arn,Values=<task-arn>

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DMS \
  --metric-name CDCLatencySource
```

### Run Glue ETL Job
```bash
# Start ETL job
aws glue start-job-run --job-name autocorp-sales-order-hudi-etl

# Check job status
aws glue get-job-run --job-name autocorp-sales-order-hudi-etl --run-id <run-id>
```

### Data Quality Testing Workflow

**1. Generate test data with data quality issues:**
```bash
python generate_sales_orders_csv.py
```

Outputs:
- `sales_orders.csv` - 791,532 orders with injected issues
- `sales_order_parts.csv` - Parts line items
- `sales_order_services.csv` - Service line items
- `data_validation_manifest.json` - Expected issue counts

**2. Configure data quality parameters in script:**
```python
# Missing values (set to 0.0 for clean data)
MISSING_CUSTOMER_ID_RATE = 0.007      # 0.7%
MISSING_ORDER_DATE_RATE = 0.0002      # 0.02%
MISSING_TAX_RATE = 0.001              # 0.1%

# Invalid data
INVALID_DATE_FORMAT_RATE = 0.0008     # 0.08%
FORMATTED_NUMBER_RATE = 0.0015        # 0.15%

# Edge cases
DUPLICATE_ORDER_ID_RATE = 0.0001      # 0.01%
NEGATIVE_AMOUNT_RATE = 0.0005         # 0.05%
```

**3. Upload to S3 via DataSync and run Glue Crawler**

**4. Validate pipeline behavior:**
- Check schema inference (are nulls handled correctly?)
- Verify data type detection (STRING vs. DOUBLE/TIMESTAMP?)
- Compare actual vs. expected issue counts from manifest
- Validate data cleansing and transformation logic

**See `DATA_QUALITY_TESTING.md` for comprehensive testing guide.**

## Common Database Operations

### View Database Status
```bash
psql -U scotton -d autocorp -c "
  SELECT 'auto_parts' as table_name, COUNT(*) FROM auto_parts 
  UNION ALL SELECT 'customers', COUNT(*) FROM customers 
  UNION ALL SELECT 'service', COUNT(*) FROM service 
  UNION ALL SELECT 'service_parts', COUNT(*) FROM service_parts
  ORDER BY table_name;"
```

### Query Example: Get Service with Parts
```sql
SELECT 
    s.service,
    s.category,
    s.labor_cost,
    sp.sku,
    sp.quantity
FROM service s
JOIN service_parts sp ON s.serviceid = sp.serviceid
WHERE s.serviceid = '48392017';
```

### Create a Sample Order
```sql
-- Insert order header
INSERT INTO sales_order (customer_id, order_date, invoice_number, 
                         payment_method, total_amount, order_type)
VALUES (1, CURRENT_TIMESTAMP, 'INV-2025-001', 'Credit Card', 
        145.80, 'Service')
RETURNING order_id;

-- Insert service line item
INSERT INTO sales_order_services (order_id, serviceid, labor_minutes, 
                                   labor_cost, parts_cost, line_total)
VALUES (1, '48392017', 30, 45.00, 90.00, 135.00);
```

## Service Categories

The system includes 110 services across these categories:
- Engine & Powertrain
- Transmission & Drivetrain
- Tires & Wheels
- Brakes
- Cooling System
- Electrical System
- HVAC
- Suspension & Steering
- General Preventive Maintenance
- Exhaust & Emissions
- Fluids & Filters

## Data Statistics

- **Average parts per service:** ~9.8 parts
- **Service with most parts:** ID `92038482` (27 parts)
- **Customer geographic spread:** 59 different states
- **Total service-parts relationships:** 1,074
- **Total orders (PostgreSQL):** 397,146 orders
- **Total orders (CSV files):** 791,532 unique orders (1,864,774 rows with intentional duplicates)
- **Combined dataset:** 1,188,678 unique orders for DMS/DataSync testing
- **Data quality demonstration:** CSV duplicates showcase ETL deduplication with Hudi upserts

## Technical Deep Dive

### Data Lakehouse Architecture
See **`developer-approach.md`** (850 lines) for:
- Complete technical architecture and design decisions
- AWS DMS, DataSync, Glue ETL implementation details
- Apache Hudi configuration and PySpark code examples
- Performance tuning, security, and scalability strategies
- 4-week implementation timeline

### Infrastructure as Code
See **`IAC_FEASIBILITY_ASSESSMENT.md`** (588 lines) for:
- Service-by-service IaC feasibility analysis (S3, Glue, DMS, DataSync)
- Terraform vs CloudFormation comparison
- Cost estimation ($86-151/month for dev environment)
- Security considerations and state management
- Manual steps and automation coverage (95%)

### Project Timeline
See **`PROJECT_GANTT_CHART.md`** (307 lines) for:
- 4-week project timeline with visual progress bars
- Current status: Phase 1 (80% complete)
- Detailed task breakdown by phase
- Risk register and mitigation strategies
- Resource allocation and cost tracking

## Complete Documentation Index

### Architecture & Design
1. **`developer-approach.md`** (850 lines) - Comprehensive technical architecture
   - Data lakehouse design with AWS services
   - CDC replication strategy with DMS
   - Apache Hudi implementation with PySpark
   - Infrastructure as Code approach
   - 4-week implementation timeline

2. **`IAC_FEASIBILITY_ASSESSMENT.md`** (588 lines) - IaC analysis
   - Terraform feasibility for DMS, DataSync, Glue, S3
   - Cost estimation and optimization strategies
   - Security and state management
   - Manual steps and automation coverage

3. **`PROJECT_GANTT_CHART.md`** (307 lines) - Project tracking
   - Visual timeline with progress indicators
   - Phase-by-phase task breakdown
   - Risk register and mitigation plans
   - Current status: 20% complete (Phase 1)

### Infrastructure
4. **`terraform/README.md`** (297 lines) - Deployment guide
   - Terraform structure and module documentation
   - Deployment instructions for dev/staging/prod
   - Troubleshooting and maintenance procedures

### Database & SQL
5. **`DATABASE_STATUS.md`** - Schema details and statistics
6. **`SALES_SYSTEM_USAGE.md`** - SQL query examples (10+ queries)

### Analytics Layer
7. **`ANALYTICS_LAYER.md`** (479 lines) - Analytics layer documentation
   - Denormalized wide tables for BI and analytics
   - 8+ query examples with performance comparisons
   - ETL pipeline architecture and scheduling
   - Performance benefits: 80%+ faster queries, 68% cost savings
   - Best practices and monitoring guidance

### AI & Machine Learning (Phase 5)
8. **`DEPLOYMENT_SUMMARY.md`** - AI chatbox deployment summary
   - Live URL and deployment details
   - Infrastructure deployed (S3 static hosting)
   - Testing checklist and redeployment script

9. **`frontend/autocorp-chatbox/IMPLEMENTATION.md`** - Frontend implementation guide
   - React component code (ChatBox, MessageList, InputBar, ChatHeader)
   - API client integration with Bedrock
   - AWS deployment instructions

10. **`docs/parts_selection_and_correction.md`** (253 lines) - Parts selection guide
   - How RAG retrieval works for service queries
   - Complete data flow: PostgreSQL → Enrichment → S3 → Bedrock
   - 7-step correction process for incorrect part mappings
   - Best practices and troubleshooting

## Project Status

**Current Phase:** Phase 5 Complete - AI Chatbox Deployed

**Progress:** 100% Complete (30 of 30 days)

**Completed:**
- ✅ **Phase 1:** PostgreSQL database + Terraform IaC (100%)
- ✅ **Phase 2:** Glue ETL jobs + Data Catalog (100%)
- ✅ **Phase 2.5:** Production data generation (100%)
  - PostgreSQL: 397K orders (1.6M total rows)
  - CSV files: 792K unique orders (1.86M rows with intentional duplicates, 7.27M total)
  - Combined: 1.19M unique orders across both sources
  - Data quality testing: CSV duplicates demonstrate Hudi deduplication
- ✅ **Phase 3:** DMS & DataSync IaC (100%)
  - DMS Terraform module complete (361 lines)
  - PostgreSQL CDC configured
  - Ready for deployment (execution deferred)
- ✅ **Phase 4:** Analytics & Query Layer (100%)
  - Athena workgroup with 5 named queries
  - CloudWatch monitoring and alarms
  - 3 analytics ETL jobs deployed
- ✅ **Phase 5:** AI Chatbox (100%)
  - Bedrock Nova Pro with RAG operational
  - Lambda + API Gateway deployed and tested (3-second response times)
  - Next.js frontend deployed to S3 static hosting
  - Live URL: http://autocorp-frontend-dev.s3-website-us-east-1.amazonaws.com
- ✅ Infrastructure deployed: 119 AWS resources via Terraform
- ✅ Glue ETL jobs: 11 jobs operational with Apache Hudi
- ✅ Data Quality: 35+ validation rules implemented

**What Works Right Now:**
1. Complete data lakehouse with S3, Glue, Athena
2. Apache Hudi tables with ACID transactions
3. Bedrock Nova Pro AI with 1,584 documents indexed
4. API Gateway endpoints responding in ~3 seconds
5. 🌐 **Live AI Chatbox:** http://autocorp-frontend-dev.s3-website-us-east-1.amazonaws.com

**Deployment Complete:**
- ✅ Frontend deployed to S3 static website hosting
- 🌐 **Live URL:** http://autocorp-frontend-dev.s3-website-us-east-1.amazonaws.com
- **Note:** Alternative deployment method used (S3 instead of Amplify) to avoid GitHub OAuth requirement
- See `docs/amplify_deployment_guide.md` for Amplify Console deployment instructions

**Latest Update (Jan 2, 2026):**
- 📖 Added comprehensive parts selection and correction guide
- 🔍 Documented RAG retrieval process for service queries
- 🛠️ Created step-by-step guide to fix incorrect service-part mappings

**Timeline:** 6 weeks (Nov 18, 2025 - Jan 2, 2026) - Core platform complete!

## Technology Stack

### Cloud & Infrastructure
- **AWS Services:** DMS, DataSync, Glue, S3, Athena, Bedrock, Lambda, API Gateway, Amplify
- **IaC:** Terraform 1.5+ with AWS Provider 5.0
- **Open Table Formats:** Apache Hudi 0.14+
- **Query Engine:** AWS Athena (Presto/Trino)
- **AI/ML:** Amazon Bedrock Nova Pro with RAG (Phase 5)

### Data Engineering
- **ETL:** AWS Glue with PySpark
- **CDC:** AWS DMS with logical replication
- **File Formats:** Parquet (columnar), Hudi (ACID)
- **Compression:** SNAPPY for optimal performance

### Database
- **RDBMS:** PostgreSQL (source system)
- **Tables:** 7 (auto_parts, customers, service, service_parts, sales_order, sales_order_parts, sales_order_services)
- **Data Volume:** 1.6M rows in PostgreSQL + 7.27M rows in CSV files (1.19M unique orders)

### Development
- **Languages:** Python 3.12+, SQL, HCL (Terraform), TypeScript (Phase 5)
- **Frontend:** Next.js 14+, React, Tailwind CSS (Phase 5)
- **Version Control:** Git with .gitignore for sensitive files
- **Documentation:** Markdown (2,800+ lines)

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contact

Project Owner: scotton

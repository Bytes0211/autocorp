# AutoCorp Data Lake Pipeline - Process Flow Diagram

**Project:** AutoCorp Cloud Data Lakehouse  
**Created:** December 7, 2025  
**Last Updated:** December 16, 2025  
**Version:** 1.1

---

## 1. High-Level Data Flow Architecture

```mermaid
flowchart TB
    subgraph Sources["Data Sources"]
        PG[(PostgreSQL DB<br/>300K orders)]
        CSV[CSV Files<br/>700K orders]
    end
    
    subgraph Ingestion["Data Ingestion Layer"]
        DMS[AWS DMS<br/>CDC Replication]
        DS[AWS DataSync<br/>File Transfer]
    end
    
    subgraph Raw["S3 Raw Zone"]
        RawDB[raw/database/<br/>Parquet]
        RawCSV[raw/csv/<br/>CSV files]
    end
    
    subgraph Catalog["AWS Glue Catalog"]
        Crawler1[Crawler: raw-database]
        Crawler2[Crawler: raw-csv]
        GlueCatalog[(Glue Data Catalog<br/>Schema Registry)]
    end
    
    subgraph Transform["ETL Processing Layer"]
        ETL1[Glue ETL Job<br/>sales_order]
        ETL2[Glue ETL Job<br/>customers]
        ETL3[Glue ETL Job<br/>auto_parts]
        ETL4[Glue ETL Job<br/>service]
        ETL5[Glue ETL Job<br/>service_parts]
        ETL6[Glue ETL Job<br/>sales_order_parts]
        ETL7[Glue ETL Job<br/>sales_order_services]
    end
    
    subgraph Curated["S3 Curated Zone"]
        Hudi[Apache Hudi Tables<br/>ACID + Time Travel<br/>1M orders unified]
    end
    
    subgraph Analytics["Query Layer"]
        Athena[AWS Athena<br/>SQL Queries]
        BI[BI Tools<br/>Tableau/QuickSight]
    end
    
    PG -->|Real-time CDC| DMS
    CSV -->|Batch Sync| DS
    DMS -->|Parquet| RawDB
    DS -->|CSV| RawCSV
    RawDB --> Crawler1
    RawCSV --> Crawler2
    Crawler1 --> GlueCatalog
    Crawler2 --> GlueCatalog
    GlueCatalog --> ETL1 & ETL2 & ETL3 & ETL4 & ETL5 & ETL6 & ETL7
    ETL1 & ETL2 & ETL3 & ETL4 & ETL5 & ETL6 & ETL7 --> Hudi
    Hudi --> Athena
    Athena --> BI
    
    style PG fill:#e1f5ff
    style CSV fill:#e1f5ff
    style DMS fill:#fff4e6
    style DS fill:#fff4e6
    style Hudi fill:#e8f5e9
    style Athena fill:#f3e5f5
```

---

## 2. Project Phase Flow

```mermaid
flowchart LR
    subgraph Phase1["Phase 1: Foundation<br/>(Nov 18-22)"]
        P1A[Database Setup]
        P1B[IaC Development]
        P1C[Terraform Deploy]
    end
    
    subgraph Phase2["Phase 2: Glue ETL<br/>(Nov 25 - Dec 7)"]
        P2A[Create ETL Scripts]
        P2B[Deploy Glue Jobs]
        P2C[Data Quality Rules]
        P2D[End-to-End Testing]
    end
    
    subgraph Phase25["Phase 2.5: Data Prep<br/>(Dec 7-8)"]
        P25A[Generate PostgreSQL<br/>300K orders]
        P25B[Generate CSV<br/>700K orders]
        P25C[Validate Data]
    end
    
    subgraph Phase3["Phase 3: DMS IaC<br/>(Dec 7-16)"]
        P3A[Configure PostgreSQL<br/>Logical Replication]
        P3B[DMS Terraform Module<br/>361 lines]
        P3C[DataSync Documentation<br/>Production Guide]
        P3D[Phase 3 IaC Complete]
    end
    
    subgraph Phase4["Phase 4: Analytics<br/>(Dec 16-20)"]
        P4A[Analytics ETL Jobs<br/>3 scripts created]
        P4B[Configure Athena<br/>Workgroups]
        P4C[Query Optimization<br/>Partitioning]
        P4D[Documentation<br/>Finalization]
    end
    
    P1A --> P1B --> P1C
    P1C --> P2A
    P2A --> P2B --> P2C --> P2D
    P2D --> P25A
    P25A --> P25B --> P25C
    P25C --> P3A
    P3A --> P3B --> P3C --> P3D
    P3D --> P4A
    P4A --> P4B --> P4C --> P4D
    
    style Phase1 fill:#c8e6c9
    style Phase2 fill:#c8e6c9
    style Phase25 fill:#c8e6c9
    style Phase3 fill:#c8e6c9
    style Phase4 fill:#fff9c4
```

---

## 3. Data Generation & Loading Flow (Phase 2.5)

```mermaid
flowchart TD
    Start([Start: Phase 2.5])
    
    Script[Update generate_sales_orders.py<br/>Add --target parameter]
    
    Decision{Target?}
    
    GenPG[Generate 300K Orders<br/>to PostgreSQL]
    ValidPG[Validate PostgreSQL Data<br/>Referential Integrity]
    
    GenCSV[Generate 700K Orders<br/>to CSV Files]
    StageCSV[Stage CSV Files<br/>/data/autocorp/sales_archives/]
    
    TestETL[Test 3 Sales ETL Jobs<br/>with New Data]
    
    Complete([Phase 2.5 Complete<br/>Ready for Phase 3])
    
    Start --> Script
    Script --> Decision
    Decision -->|postgres| GenPG
    Decision -->|csv| GenCSV
    GenPG --> ValidPG
    GenCSV --> StageCSV
    ValidPG --> TestETL
    StageCSV --> TestETL
    TestETL --> Complete
    
    style Start fill:#4caf50,color:#fff
    style Complete fill:#4caf50,color:#fff
    style Decision fill:#ff9800,color:#fff
```

---

## 4. DMS CDC Replication Flow (Phase 3 - IaC Ready)

**Status:** Infrastructure as Code complete, ready for deployment

```mermaid
flowchart TB
    subgraph PostgreSQL["PostgreSQL Database"]
        PG_Data[(sales_order<br/>sales_order_parts<br/>sales_order_services<br/>300K orders)]
        PG_Logical[Logical Replication<br/>✅ Configured]
    end
    
    subgraph DMS["AWS DMS (IaC Ready)"]
        DMS_Instance[DMS Replication Instance<br/>dms.t3.medium<br/>📝 Terraform defined]
        Source_EP[Source Endpoint<br/>PostgreSQL<br/>📝 Terraform defined]
        Target_EP[Target Endpoint<br/>S3 Parquet<br/>📝 Terraform defined]
        Task[DMS Task<br/>Full Load + CDC<br/>📝 Terraform defined]
        TableMap[Table Mappings<br/>7 tables<br/>📝 JSON configured]
    end
    
    subgraph S3Raw["S3 Raw Zone"]
        S3_Parquet[raw/database/<br/>Parquet Files<br/>300K orders]
    end
    
    subgraph Glue["AWS Glue"]
        Crawler[Glue Crawler<br/>Schema Discovery]
        ETL[Glue ETL Jobs<br/>Hudi Upserts]
    end
    
    subgraph Hudi["S3 Curated Zone"]
        HudiTables[Apache Hudi Tables<br/>ACID Transactions]
    end
    
    PG_Data --> PG_Logical
    PG_Logical --> Source_EP
    Source_EP --> DMS_Instance
    DMS_Instance --> Target_EP
    TableMap --> Task
    Task --> Target_EP
    Target_EP -->|Parquet| S3_Parquet
    S3_Parquet --> Crawler
    Crawler --> ETL
    ETL -->|Upsert| HudiTables
    
    PG_Data -.->|INSERT/UPDATE/DELETE| PG_Logical
    PG_Logical -.->|CDC Stream<br/>&lt;5 min lag| Task
    
    style PG_Data fill:#e3f2fd
    style Task fill:#fff3e0
    style HudiTables fill:#e8f5e9
```

---

## 5. DataSync File Transfer Flow (Phase 3 - Documented)

**Status:** Production deployment guide documented, S3 CLI alternative for dev

```mermaid
flowchart TB
    subgraph OnPrem["On-Premises/Local"]
        CSV_Files[CSV Files<br/>700K orders<br/>/data/autocorp/sales_archives/]
        Agent[DataSync Agent<br/>📝 Deployment guide]
    end
    
    subgraph AWS["AWS Cloud"]
        DataSync[AWS DataSync Service<br/>📝 Documented]
        Location_Source[Source Location<br/>NFS/SMB<br/>📝 Config ready]
        Location_Target[Target Location<br/>S3<br/>📝 Config ready]
        Task[DataSync Task<br/>Scheduled Transfer<br/>📝 Documented]
    end
    
    subgraph S3["S3 Raw Zone"]
        S3_CSV[raw/csv/<br/>700K orders]
    end
    
    subgraph Processing["Processing"]
        Crawler2[Glue Crawler<br/>raw-csv]
        ETL_CSV[Glue ETL Jobs<br/>Process CSV]
        Hudi2[Apache Hudi Tables<br/>Merge with DMS data]
    end
    
    CSV_Files --> Agent
    Agent --> Location_Source
    Location_Source --> DataSync
    DataSync --> Task
    Task --> Location_Target
    Location_Target --> S3_CSV
    S3_CSV --> Crawler2
    Crawler2 --> ETL_CSV
    ETL_CSV --> Hudi2
    
    style CSV_Files fill:#e1f5ff
    style Task fill:#fff3e0
    style Hudi2 fill:#e8f5e9
```

---

## 6. ETL Job Processing Flow

```mermaid
flowchart TD
    Start([ETL Job Triggered])
    
    Read[Read from Glue Catalog<br/>Source: raw/database/ or raw/csv/]
    
    Transform{Data Transformations}
    
    Dedupe[Deduplication<br/>By Primary Key]
    Quality[Data Quality Checks<br/>35+ Validations]
    Format[Format Conversions<br/>Timestamp, Partitions]
    
    Hudi{Hudi Operation}
    
    Insert[Insert New Records]
    Upsert[Upsert Existing Records]
    
    Write[Write to S3 Curated Zone<br/>Apache Hudi Format]
    
    Metadata[Update Hudi Metadata<br/>.hoodie/ directory]
    
    Sync[Hive Metastore Sync<br/>Optional]
    
    Complete([Job Complete<br/>CloudWatch Logged])
    
    Start --> Read
    Read --> Transform
    Transform --> Dedupe
    Dedupe --> Quality
    Quality --> Format
    Format --> Hudi
    Hudi --> Insert
    Hudi --> Upsert
    Insert --> Write
    Upsert --> Write
    Write --> Metadata
    Metadata --> Sync
    Sync --> Complete
    
    style Start fill:#4caf50,color:#fff
    style Complete fill:#4caf50,color:#fff
    style Quality fill:#ff9800,color:#fff
    style Write fill:#2196f3,color:#fff
```

---

## 7. Hudi Table Strategy Flow

```mermaid
flowchart LR
    subgraph TableTypes["Table Types"]
        Transactional[Transactional Tables<br/>sales_order<br/>sales_order_parts<br/>sales_order_services]
        Dimension[Dimension Tables<br/>customers<br/>auto_parts<br/>service<br/>service_parts]
    end
    
    subgraph HudiFormat["Hudi Table Format"]
        COW[Copy-on-Write<br/>COW<br/>Better for read-heavy]
        MOR[Merge-on-Read<br/>MOR<br/>Better for write-heavy]
    end
    
    subgraph Operations["Supported Operations"]
        Op1[Inserts]
        Op2[Updates]
        Op3[Deletes]
        Op4[Upserts]
        Op5[Time Travel Queries]
    end
    
    Transactional --> COW
    Dimension --> MOR
    COW --> Op1 & Op2 & Op3 & Op4 & Op5
    MOR --> Op1 & Op2 & Op3 & Op4 & Op5
    
    style COW fill:#bbdefb
    style MOR fill:#c5e1a5
```

---

## 8. Query Layer Flow (Phase 4 - In Progress)

**Status:** Analytics ETL scripts created, Athena configuration in progress

```mermaid
flowchart TB
    subgraph Storage["S3 Curated Zone"]
        Hudi[(Apache Hudi Tables<br/>Operational: 7 tables<br/>Analytics: 3 new tables<br/>1M orders unified)]
    end
    
    subgraph Catalog["AWS Glue"]
        GlueCat[(Glue Data Catalog<br/>Table Schemas<br/>Partition Info)]
    end
    
    subgraph Query["AWS Athena"]
        Athena[Athena Query Engine<br/>Presto/Trino]
        Workgroup[Workgroup: autocorp-dev]
    end
    
    subgraph Queries["Query Types"]
        Q1[Standard SQL Queries<br/>SELECT, JOIN, AGG]
        Q2[Time Travel Queries<br/>Query as of timestamp]
        Q3[Incremental Queries<br/>Only changed records]
    end
    
    subgraph BI["Analytics & BI"]
        QuickSight[Amazon QuickSight]
        Tableau[Tableau]
        PowerBI[Power BI]
    end
    
    Hudi --> GlueCat
    GlueCat --> Athena
    Athena --> Workgroup
    Workgroup --> Q1 & Q2 & Q3
    Q1 --> QuickSight & Tableau & PowerBI
    Q2 --> QuickSight & Tableau & PowerBI
    Q3 --> QuickSight & Tableau & PowerBI
    
    style Hudi fill:#e8f5e9
    style Athena fill:#f3e5f5
    style BI fill:#fff9c4
```

---

## 9. Complete End-to-End Flow with Timing

```mermaid
flowchart TB
    subgraph Input["Data Sources"]
        PG[PostgreSQL<br/>300K orders<br/>Real-time]
        CSV[CSV Files<br/>700K orders<br/>Batch]
    end
    
    subgraph Ingest["Ingestion<br/>(Minutes)"]
        DMS[DMS CDC<br/>&lt;5 min lag]
        DS[DataSync<br/>Hourly sync]
    end
    
    subgraph RawZone["Raw Zone<br/>(Seconds)"]
        S3Raw[S3 Raw<br/>Parquet/CSV]
    end
    
    subgraph Discover["Discovery<br/>(Minutes)"]
        Crawl[Glue Crawlers<br/>Schema detection]
    end
    
    subgraph Process["Processing<br/>(2-5 min per job)"]
        ETL[7 Glue ETL Jobs<br/>PySpark + Hudi]
    end
    
    subgraph CuratedZone["Curated Zone<br/>(Seconds)"]
        S3Hudi[S3 Curated<br/>Hudi Tables<br/>1M orders]
    end
    
    subgraph QueryLayer["Query<br/>(&lt;30 sec)"]
        Athena[Athena<br/>SQL Queries]
    end
    
    subgraph Results["Results"]
        Output[Analytics<br/>Dashboards<br/>Reports]
    end
    
    PG -->|Real-time| DMS
    CSV -->|Scheduled| DS
    DMS & DS --> S3Raw
    S3Raw --> Crawl
    Crawl --> ETL
    ETL --> S3Hudi
    S3Hudi --> Athena
    Athena --> Output
    
    PG -.->|End-to-End:<br/>&lt;15 minutes| Output
    CSV -.->|End-to-End:<br/>Hourly + 15 min| Output
    
    style PG fill:#e3f2fd
    style CSV fill:#e3f2fd
    style S3Hudi fill:#e8f5e9
    style Output fill:#fff9c4
```

---

## 10. Infrastructure Deployment Flow

```mermaid
flowchart TD
    Start([Start Deployment])
    
    Backend[Create Terraform Backend<br/>S3 + DynamoDB]
    
    Init[terraform init]
    
    Phase1{Phase 1:<br/>Foundation}
    
    S3[Deploy S3 Module<br/>Data Lake Buckets]
    IAM[Deploy IAM Module<br/>Service Roles]
    Secrets[Deploy Secrets Module<br/>Credentials]
    
    Phase2{Phase 2:<br/>Glue ETL}
    
    Glue[Deploy Glue Module<br/>Catalog + Crawlers + ETL Jobs]
    Scripts[Upload PySpark Scripts<br/>to S3]
    Test[Test ETL Jobs<br/>End-to-End]
    
    Phase3{Phase 3:<br/>Replication}
    
    DMS_Mod[Deploy DMS Module<br/>Replication Instance]
    DataSync_Mod[Deploy DataSync Module<br/>Agents + Tasks]
    
    Phase4{Phase 4:<br/>Analytics}
    
    Athena_Mod[Configure Athena<br/>Workgroups + Queries]
    Monitor[Deploy CloudWatch<br/>Dashboards + Alarms]
    
    Complete([Deployment Complete<br/>Production Ready])
    
    Start --> Backend
    Backend --> Init
    Init --> Phase1
    Phase1 --> S3 & IAM & Secrets
    S3 & IAM & Secrets --> Phase2
    Phase2 --> Glue
    Glue --> Scripts
    Scripts --> Test
    Test --> Phase3
    Phase3 --> DMS_Mod & DataSync_Mod
    DMS_Mod & DataSync_Mod --> Phase4
    Phase4 --> Athena_Mod & Monitor
    Athena_Mod & Monitor --> Complete
    
    style Start fill:#4caf50,color:#fff
    style Complete fill:#4caf50,color:#fff
    style Phase1 fill:#2196f3,color:#fff
    style Phase2 fill:#2196f3,color:#fff
    style Phase3 fill:#ff9800,color:#fff
    style Phase4 fill:#ff9800,color:#fff
```

---

## Diagram Descriptions

### 1. High-Level Data Flow Architecture
Shows the complete data flow from source systems through ingestion, transformation, and query layers.

### 2. Project Phase Flow
Illustrates the sequential progression through all project phases with dependencies.

### 3. Data Generation & Loading Flow (Phase 2.5)
Details the current data preparation step including PostgreSQL and CSV generation.

### 4. DMS CDC Replication Flow (Phase 3)
Shows how PostgreSQL data is replicated to S3 via DMS with CDC.

### 5. DataSync File Transfer Flow (Phase 3)
Illustrates the batch file transfer process from on-premises to S3.

### 6. ETL Job Processing Flow
Details the internal logic of Glue ETL jobs including transformations and Hudi operations.

### 7. Hudi Table Strategy Flow
Explains the decision logic for COW vs MOR table formats.

### 8. Query Layer Flow (Phase 4)
Shows how Athena queries Hudi tables and integrates with BI tools.

### 9. Complete End-to-End Flow with Timing
Provides timing expectations for each stage of the pipeline.

### 10. Infrastructure Deployment Flow
Maps out the Terraform deployment sequence across all phases.

---

## Legend

- **Green boxes**: Start/End points, completed phases
- **Blue boxes**: Infrastructure components
- **Orange boxes**: Decision points, in-progress phases
- **Light blue**: Data storage layers
- **Light green**: Hudi/curated zone
- **Light yellow**: Analytics/BI layer
- **Dotted lines**: Data flow paths or timing indicators
- **Solid lines**: Process flow or dependencies

---

## Usage Notes

These diagrams are written in Mermaid format and can be rendered in:
- GitHub markdown files
- VS Code with Mermaid extension
- Mermaid Live Editor (https://mermaid.live/)
- Documentation tools like Confluence with Mermaid support
- Draw.io (import Mermaid)

To view these diagrams, paste the code blocks into any Mermaid-compatible viewer.

---

---

## Document Change Log

### Version 1.1 (December 16, 2025)
- Updated Phase 3 to reflect IaC completion (DMS Terraform module, PostgreSQL CDC config, DataSync docs)
- Updated Phase 4 to show analytics layer in progress (3 ETL scripts created)
- Changed phase color coding to reflect completion status
- Added status notes to DMS, DataSync, and Query Layer sections
- Updated dates to reflect actual project timeline

### Version 1.0 (December 7, 2025)
- Initial process flow diagram creation
- 10 comprehensive flow diagrams
- Complete end-to-end architecture documentation

---

**Document Version:** 1.1  
**Last Updated:** December 16, 2025  
**Created:** December 7, 2025  
**Author:** scotton  
**Project:** AutoCorp Data Lake Pipeline  
**Status:** Phase 3 Complete (IaC) | Phase 4 Analytics Layer In Progress

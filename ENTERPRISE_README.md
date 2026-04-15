# AutoCorp Enterprise Data Platform

**Executive Summary**

AutoCorp is a production-ready **cloud-native data lakehouse platform** with integrated **AI-powered customer support**. Built on AWS, it demonstrates enterprise-grade data engineering, real-time analytics, and conversational AI capabilities.

🌐 **Live Demo:** http://autocorp-frontend-dev.s3-website-us-east-1.amazonaws.com

---

## Platform Capabilities

### AI-Powered Customer Support
- **Intelligent Chatbox** powered by Amazon Bedrock Nova Pro
- **RAG (Retrieval-Augmented Generation)** with 1,584 indexed documents
- **Natural language queries** for auto parts, services, and pricing
- **3-second average response time** with semantic search via OpenSearch

### Data Lakehouse Architecture
- **Apache Hudi tables** with ACID transactions and time-travel queries
- **Sub-15 minute data latency** from source to queryable
- **1.6M+ records** across 7 operational tables
- **Serverless ETL** with AWS Glue PySpark jobs

### Real-Time Analytics
- **AWS Athena** for SQL analytics directly on data lake
- **Pre-built dashboards** with CloudWatch monitoring
- **Denormalized analytics layer** for 80%+ faster BI queries
- **Time-travel queries** for historical analysis

### Infrastructure as Code
- **119 AWS resources** deployed via Terraform
- **95% automation** (only DataSync agent requires manual setup)
- **Multi-environment support** (dev/staging/prod)
- **Cost-optimized** with lifecycle policies and right-sized instances

---

## Technical Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │────▶│    AWS DMS      │────▶│   S3 Data Lake  │
│   (Source DB)   │     │   (CDC <5min)   │     │   (Raw Zone)    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────▼────────┐
                        │              AWS Glue                    │
                        │   11 ETL Jobs | 3 Crawlers | Hudi Tables │
                        └────────────────────────────┬─────────────┘
                                                     │
┌─────────────────┐     ┌─────────────────┐     ┌────▼────────────┐
│   Next.js UI    │◀────│  API Gateway    │◀────│  AWS Lambda     │
│ (S3 Hosting)    │     │  (REST API)     │     │  (Python 3.12)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────▼────────┐
                        │           Amazon Bedrock                 │
                        │   Nova Pro LLM | Knowledge Base | RAG    │
                        │         OpenSearch Serverless            │
                        └──────────────────────────────────────────┘
```

---

## AWS Services Deployed

| Service | Purpose | Status |
|---------|---------|--------|
| **Amazon S3** | Data lake with raw/curated zones | ✅ Operational |
| **AWS Glue** | ETL with 11 PySpark jobs | ✅ Operational |
| **Amazon Athena** | Serverless SQL analytics | ✅ Operational |
| **Amazon Bedrock** | AI/ML with Nova Pro + RAG | ✅ Operational |
| **OpenSearch Serverless** | Vector database for semantic search | ✅ Operational |
| **AWS Lambda** | Serverless API functions | ✅ Operational |
| **API Gateway** | REST API with CORS + rate limiting | ✅ Operational |
| **AWS DMS** | CDC replication (IaC ready) | 📝 Ready |
| **CloudWatch** | Monitoring, dashboards, alarms | ✅ Operational |
| **Secrets Manager** | Credential management | ✅ Operational |

---

## AI Chatbox Features

### What Users Can Ask
- "What parts are needed for an oil change?"
- "Show me brake service pricing"
- "What services are available for my vehicle?"
- "Tell me about battery replacement"

### Technical Specifications
- **Model:** Amazon Bedrock Nova Pro
- **Embeddings:** Titan Embeddings G1 (1,536 dimensions)
- **Vector Store:** OpenSearch Serverless (2GB collection)
- **Knowledge Base:** 1,584 documents (parts, services, service-parts mappings)
- **Response Time:** ~3 seconds (p95)
- **Rate Limit:** 100 requests/minute per API key

### API Endpoints
```bash
# Chat endpoint
POST https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev/chat
Content-Type: application/json
x-api-key: <api-key>

{"message": "What parts are needed for an oil change?"}

# Analytics endpoint
POST https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev/analytics
```

---

## Data Assets

### Source Database (PostgreSQL)
| Table | Records | Description |
|-------|---------|-------------|
| `customers` | 1,149 | Customer profiles |
| `auto_parts` | 400 | Parts inventory |
| `service` | 110 | Service catalog (11 categories) |
| `service_parts` | 1,074 | Service-to-parts mappings |
| `sales_order` | 397,146 | Order headers |
| `sales_order_parts` | 853,591 | Parts line items |
| `sales_order_services` | 355,067 | Service line items |
| **Total** | **1,605,804** | |

### Knowledge Base (RAG)
- **Auto parts:** 400 items with SKU, name, category, price
- **Services:** 110 services across 11 categories
- **Mappings:** 1,074 service-to-parts relationships
- **Format:** JSONL with semantic enrichment for RAG optimization

---

## Cost Profile (Development Environment)

| Component | Monthly Cost |
|-----------|--------------|
| S3 Storage + Requests | $5-10 |
| Glue ETL Jobs | $10-20 |
| Athena Queries | $5-10 |
| Bedrock API | $8-15 |
| OpenSearch Serverless | $140 |
| Lambda + API Gateway | $5-10 |
| CloudWatch | $3-5 |
| **Total** | **~$180-210/month** |

*Note: OpenSearch Serverless is the primary cost driver. Consider time-based scaling for non-production environments.*

---

## Security & Compliance

### Authentication & Authorization
- API key authentication (development)
- IAM least-privilege roles for all services
- Secrets Manager for credential storage
- CORS configured for allowed origins

### Data Protection
- Encryption at rest (S3 SSE, OpenSearch)
- Encryption in transit (TLS/HTTPS)
- No PII in AI chat logs
- Rate limiting (100 req/min)

### Infrastructure Security
- Remote Terraform state with S3 + DynamoDB locking
- No credentials in code or version control
- Environment-specific configurations (dev/staging/prod)

---

## Deployment

### Quick Start
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Frontend Redeployment
```bash
cd frontend/autocorp-chatbox
npm run build
aws s3 sync out/ s3://autocorp-frontend-dev/ --delete
```

### Infrastructure Status
- **119 AWS resources** deployed
- **8 Terraform modules** (S3, IAM, Secrets, Glue, Athena, Bedrock, Lambda-chat, Monitoring)
- **95% automated** deployment

---

## Project Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Infrastructure & IaC | Week 1 | ✅ Complete |
| Phase 2: Glue ETL & Data Catalog | Week 2 | ✅ Complete |
| Phase 3: DMS & DataSync IaC | Week 3 | ✅ Complete (IaC Ready) |
| Phase 4: Analytics Layer | Week 4 | ✅ Complete |
| Phase 5: AI Chatbox | Week 5-6 | ✅ Complete |

**Total Duration:** 6 weeks (Nov 18, 2025 - Jan 2, 2026)

---

## Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Detailed technical documentation |
| `DEPLOYMENT_SUMMARY.md` | Deployment details and live URL |
| `terraform/README.md` | Infrastructure deployment guide |
| `docs/parts_selection_and_correction.md` | RAG knowledge base maintenance |
| `frontend/autocorp-chatbox/IMPLEMENTATION.md` | Frontend development guide |

---

## Skills Demonstrated

### Cloud & Data Engineering
- AWS data services (S3, Glue, DMS, Athena, Bedrock)
- Apache Hudi open table format
- Serverless architecture (Lambda, API Gateway)
- Infrastructure as Code (Terraform)

### AI/ML Engineering
- Amazon Bedrock integration
- RAG (Retrieval-Augmented Generation)
- Vector databases (OpenSearch)
- Semantic search and embeddings

### Full-Stack Development
- Next.js with TypeScript
- React component architecture
- REST API design
- AWS deployment (S3 static hosting)

---

**Contact:** scotton  
**Repository:** [autocorp](https://github.com/Bytes0211/autocorp)  
**Last Updated:** February 2026

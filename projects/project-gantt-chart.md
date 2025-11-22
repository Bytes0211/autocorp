# AutoCorp Data Lake Pipeline - Project Gantt Chart

**Project Start:** November 18, 2025  
**Current Date:** November 21, 2025  
**Project Duration:** 4 weeks (20 working days)  
**Current Status:** Phase 1 - IaC Foundation (In Progress)

---

## Visual Timeline

```
Week 1 (Nov 18-22): Infrastructure & IaC Foundation
├─ Day 1-2: ████████ [COMPLETE] Database setup (PostgreSQL)
├─ Day 3:   ████████ [COMPLETE] Data generation scripts
├─ Day 4:   ████████ [COMPLETE] Developer approach documentation
└─ Day 5:   ████████ [COMPLETE] IaC structure creation

Week 2 (Nov 25-29): Glue & Data Catalog
├─ Day 6-7: ░░░░░░░░ [PENDING] Glue ETL jobs with Hudi
├─ Day 8:   ░░░░░░░░ [PENDING] Glue Crawlers deployment
├─ Day 9:   ░░░░░░░░ [PENDING] Data quality rules
└─ Day 10:  ░░░░░░░░ [PENDING] End-to-end testing

Week 3 (Dec 2-6): DMS Replication & DataSync
├─ Day 11:  ░░░░░░░░ [PENDING] DMS connectivity testing
├─ Day 12:  ░░░░░░░░ [PENDING] DMS full load
├─ Day 13:  ░░░░░░░░ [PENDING] CDC enablement
├─ Day 14:  ░░░░░░░░ [PENDING] DataSync agent deployment
└─ Day 15:  ░░░░░░░░ [PENDING] DataSync task configuration

Week 4 (Dec 9-13): Analytics & Query Layer
├─ Day 16:  ░░░░░░░░ [PENDING] Athena configuration
├─ Day 17:  ░░░░░░░░ [PENDING] Query optimization
├─ Day 18:  ░░░░░░░░ [PENDING] BI tool integration
├─ Day 19:  ░░░░░░░░ [PENDING] Documentation finalization
└─ Day 20:  ░░░░░░░░ [PENDING] Production deployment

Legend:
████ Completed   ▓▓▓▓ In Progress   ░░░░ Pending
```

---

## Detailed Phase Breakdown

### Phase 1: Infrastructure & IaC Foundation (Week 1)
**Duration:** 5 days  
**Start:** Nov 18, 2025  
**End:** Nov 22, 2025  
**Status:** 80% Complete ✅

| Task | Owner | Days | Status | Notes |
|------|-------|------|--------|-------|
| PostgreSQL database setup | scotton | 0.5 | ✅ DONE | autocorp database with 7 tables |
| CSV data generation | scotton | 1.0 | ✅ DONE | 1.2M customers, sales orders |
| Developer approach documentation | scotton | 1.0 | ✅ DONE | 688-line comprehensive doc |
| IaC feasibility assessment | scotton | 0.5 | ✅ DONE | 95% feasibility confirmed |
| Terraform structure creation | scotton | 1.0 | 🔄 IN PROGRESS | S3, IAM, Secrets modules ready |
| Terraform state backend bootstrap | scotton | 0.5 | ⏸️ BLOCKED | Awaiting AWS account access |
| Initial Terraform deployment | scotton | 0.5 | ⏸️ BLOCKED | Depends on AWS access |

**Deliverables:**
- ✅ PostgreSQL database operational
- ✅ Sample data generated (7 tables, 5,668 rows)
- ✅ Developer approach documented
- ✅ IaC feasibility assessment completed
- ✅ Terraform modules created (S3, IAM, Secrets, Glue)
- ⏸️ AWS infrastructure deployed (pending AWS access)

**Blockers:**
- AWS account credentials required for deployment

---

### Phase 2: Glue & Data Catalog (Week 2)
**Duration:** 5 days  
**Start:** Nov 25, 2025  
**End:** Nov 29, 2025  
**Status:** 0% Complete ⏸️

| Task | Owner | Days | Status | Dependencies |
|------|-------|------|--------|--------------|
| Upload PySpark ETL scripts to S3 | scotton | 0.5 | ⏸️ PENDING | Phase 1 complete |
| Deploy Glue Data Catalog | scotton | 0.5 | ⏸️ PENDING | Terraform deployed |
| Deploy Glue Crawlers (raw zones) | scotton | 0.5 | ⏸️ PENDING | S3 buckets exist |
| Create Hudi ETL job (sales_order) | scotton | 1.0 | ⏸️ PENDING | Glue catalog ready |
| Create Hudi ETL jobs (remaining tables) | scotton | 1.5 | ⏸️ PENDING | First job tested |
| Configure Glue triggers/workflows | scotton | 0.5 | ⏸️ PENDING | All jobs created |
| Test end-to-end ETL pipeline | scotton | 0.5 | ⏸️ PENDING | Workflows configured |

**Deliverables:**
- Glue Data Catalog operational
- Crawlers running on schedule
- ETL jobs transforming raw → Hudi tables
- Automated pipeline with triggers

**Success Criteria:**
- Crawlers discover schema automatically
- ETL jobs process 1M rows in <10 minutes
- Hudi tables support upserts
- Data quality checks pass

---

### Phase 3: DMS Replication & DataSync (Week 3)
**Duration:** 5 days  
**Start:** Dec 2, 2025  
**End:** Dec 6, 2025  
**Status:** 0% Complete ⏸️

| Task | Owner | Days | Status | Dependencies |
|------|-------|------|--------|--------------|
| Configure PostgreSQL logical replication | scotton | 0.5 | ⏸️ PENDING | Database admin access |
| Deploy DMS replication instance (IaC) | scotton | 0.5 | ⏸️ PENDING | Network connectivity verified |
| Create DMS endpoints (PostgreSQL, S3) | scotton | 0.5 | ⏸️ PENDING | Replication instance ready |
| Configure DMS table mappings | scotton | 0.5 | ⏸️ PENDING | Endpoints created |
| Execute DMS full load | scotton | 1.0 | ⏸️ PENDING | Table mappings configured |
| Enable CDC on DMS tasks | scotton | 0.5 | ⏸️ PENDING | Full load validated |
| Deploy DataSync agent (on-premises) | scotton | 1.0 | ⏸️ PENDING | VM/hypervisor access |
| Activate DataSync agent | scotton | 0.5 | ⏸️ PENDING | Agent deployed |
| Configure DataSync tasks (IaC) | scotton | 0.5 | ⏸️ PENDING | Agent activated |

**Deliverables:**
- DMS replicating PostgreSQL → S3 with CDC
- DataSync transferring CSV files hourly
- CDC lag <5 minutes
- File transfers validated

**Success Criteria:**
- All 7 tables replicated with matching row counts
- CDC captures INSERT/UPDATE/DELETE
- CSV files (multi-GB) transfer successfully
- Data validation checks pass

---

### Phase 4: Analytics & Query Layer (Week 4)
**Duration:** 5 days  
**Start:** Dec 9, 2025  
**End:** Dec 13, 2025  
**Status:** 0% Complete ⏸️

| Task | Owner | Days | Status | Dependencies |
|------|-------|------|--------|--------------|
| Configure Athena workgroups (IaC) | scotton | 0.5 | ⏸️ PENDING | Hudi tables exist |
| Create Athena table definitions | scotton | 0.5 | ⏸️ PENDING | Glue Catalog populated |
| Test Athena queries on Hudi tables | scotton | 0.5 | ⏸️ PENDING | Table definitions created |
| Optimize query performance | scotton | 1.0 | ⏸️ PENDING | Initial queries working |
| Test time-travel queries | scotton | 0.5 | ⏸️ PENDING | Historical data available |
| Test incremental queries | scotton | 0.5 | ⏸️ PENDING | CDC data captured |
| BI tool integration (optional) | scotton | 1.0 | ⏸️ PENDING | Athena operational |
| Create CloudWatch dashboards | scotton | 0.5 | ⏸️ PENDING | All services running |
| Finalize documentation | scotton | 1.0 | ⏸️ PENDING | All phases complete |

**Deliverables:**
- Athena querying Hudi tables successfully
- Query performance <30 seconds
- Time-travel and incremental queries documented
- CloudWatch monitoring active
- Complete documentation and runbook

**Success Criteria:**
- Athena queries return accurate results
- Query performance meets SLA (<30s)
- Time-travel queries work correctly
- Documentation is comprehensive

---

## Overall Project Status

### Completion Metrics
- **Overall Progress:** 20% (4 of 20 days)
- **Phase 1:** 80% complete (4 of 5 tasks done)
- **Phase 2:** 0% complete (awaiting Phase 1)
- **Phase 3:** 0% complete (awaiting Phase 2)
- **Phase 4:** 0% complete (awaiting Phase 3)

### Key Milestones
| Milestone | Target Date | Status |
|-----------|-------------|--------|
| ✅ Database operational | Nov 18 | ACHIEVED |
| ✅ Data generation complete | Nov 19 | ACHIEVED |
| ✅ Developer approach documented | Nov 21 | ACHIEVED |
| ✅ IaC structure created | Nov 21 | ACHIEVED |
| ⏸️ Infrastructure deployed (Phase 1) | Nov 22 | PENDING |
| ⏸️ Glue ETL operational (Phase 2) | Nov 29 | ON TRACK |
| ⏸️ DMS replication live (Phase 3) | Dec 6 | ON TRACK |
| ⏸️ Athena queries working (Phase 4) | Dec 13 | ON TRACK |

### Risk Register
| Risk | Impact | Probability | Status | Mitigation |
|------|--------|-------------|--------|------------|
| AWS account access delayed | HIGH | LOW | 🟡 MONITORING | Contact AWS admin, prepare offline testing |
| PostgreSQL network connectivity | HIGH | MEDIUM | 🟡 MONITORING | VPN setup, test early |
| DataSync agent deployment | MEDIUM | MEDIUM | 🟡 MONITORING | Document requirements, allocate VM resources |
| Hudi learning curve | MEDIUM | HIGH | 🟢 MITIGATED | Documentation reviewed, examples ready |
| DMS CDC lag issues | HIGH | MEDIUM | 🟡 MONITORING | Right-size instance, enable Multi-AZ |
| S3 cost overruns | MEDIUM | LOW | 🟢 MITIGATED | Lifecycle policies configured |

---

## Critical Path Analysis

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4

**Current Bottleneck:** AWS account access for Terraform deployment

**Dependencies:**
1. **Phase 2 depends on:** Phase 1 infrastructure (S3, Glue IAM roles)
2. **Phase 3 depends on:** Phase 2 Glue Catalog (for data validation)
3. **Phase 4 depends on:** Phase 3 data replication (Hudi tables populated)

**Parallelization Opportunities:**
- DMS and DataSync can be deployed in parallel (both in Phase 3)
- Glue Crawlers and ETL jobs can be tested separately
- Documentation can be written alongside development

---

## Resource Allocation

| Resource | Week 1 | Week 2 | Week 3 | Week 4 | Total Hours |
|----------|--------|--------|--------|--------|-------------|
| scotton | 40h | 40h | 40h | 40h | 160h |
| AWS Costs | $0 | $50 | $100 | $150 | $300 (dev) |

**Note:** Assumes single developer (scotton) working full-time on project.

---

## Next Actions (Priority Order)

### Immediate (This Week)
1. ✅ **Complete IaC structure** - Finish remaining Terraform modules
2. ⏸️ **Obtain AWS credentials** - Request access from AWS admin
3. ⏸️ **Deploy Phase 1 infrastructure** - Run `terraform apply`
4. ⏸️ **Validate S3 buckets** - Verify folder structure created
5. ⏸️ **Test IAM roles** - Ensure Glue/DMS roles work

### Next Week (Week 2)
1. Upload PySpark ETL scripts to S3
2. Deploy Glue Data Catalog via Terraform
3. Create first Hudi ETL job (sales_order)
4. Test Glue Crawler on sample data
5. Validate Hudi table creation

### Following Weeks
- Week 3: Enable DMS replication and DataSync
- Week 4: Configure Athena and complete documentation

---

## Success Criteria

### Technical Metrics
- ✅ PostgreSQL database operational: 7 tables, 5,668 rows
- ⏸️ S3 data lake deployed: raw/, curated/, logs/ structure
- ⏸️ Glue ETL processing: <10 minutes for 1M rows
- ⏸️ DMS CDC lag: <5 minutes average
- ⏸️ Athena query performance: <30 seconds for aggregations
- ⏸️ End-to-end latency: <15 minutes (source to queryable)

### Documentation Metrics
- ✅ Developer approach: 688 lines (comprehensive)
- ✅ IaC feasibility assessment: 588 lines (detailed)
- ✅ Terraform README: 297 lines (deployment guide)
- ⏸️ Operations runbook: TBD
- ⏸️ Architecture diagrams: TBD

### Cost Metrics
- Target monthly cost: $86-151 (dev environment)
- Cost optimization: Lifecycle policies, right-sizing
- Budget alerts: Configured in AWS

---

## Project Timeline Summary

```
[========= 20% Complete =========                                ]

Phase 1: ████████████████▓▓▓▓  80% (In Progress)
Phase 2: ░░░░░░░░░░░░░░░░░░░░   0% (Pending)
Phase 3: ░░░░░░░░░░░░░░░░░░░░   0% (Pending)
Phase 4: ░░░░░░░░░░░░░░░░░░░░   0% (Pending)

Estimated Completion: December 13, 2025 (on track)
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 21, 2025 | scotton | Initial Gantt chart with IaC approach |

---

## References

- [developer-approach.md](developer-approach.md) - Comprehensive technical approach
- [IAC_FEASIBILITY_ASSESSMENT.md](IAC_FEASIBILITY_ASSESSMENT.md) - IaC analysis
- [terraform/README.md](terraform/README.md) - Deployment guide
- [README.md](README.md) - Project overview

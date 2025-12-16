# Phase 5 AI Chatbox - Quick Start Guide

**Status:** Planned (After Phase 3-4 Complete)  
**Duration:** 8-10 days  
**Tech Stack:** Amazon Bedrock Nova Pro, Next.js, AWS Amplify

---

## Overview

Add an AI-powered chatbox to AutoCorp using **Amazon Bedrock Nova Pro** with **RAG** (Retrieval-Augmented Generation) for:
- Customer support (parts/services questions)
- Data analytics queries (sales trends, inventory)
- Natural language interface to your data lake

---

## Architecture Summary

```
User → Amplify (Next.js) → API Gateway → Lambda → Bedrock Nova Pro
                                                       ↓
                                                  Knowledge Base
                                                       ↓
                                              S3 Data Lake (RAG)
```

---

## Prerequisites

Before starting Phase 5:
- ✅ Phase 1-4 complete (data lake operational)
- ✅ Athena queries working
- ✅ Node.js 18+ installed locally
- ✅ AWS Amplify CLI installed
- ✅ Bedrock model access granted

---

## Quick Start Commands

### 1. Request Bedrock Access
```bash
# Request model access in AWS Console
# Go to: Bedrock → Model access → Request access to "Nova Pro"
```

### 2. Deploy Backend (Terraform)
```bash
cd terraform
terraform init
terraform plan -target=module.bedrock
terraform apply -target=module.bedrock

terraform plan -target=module.lambda_chat
terraform apply -target=module.lambda_chat
```

### 3. Create Frontend
```bash
cd /home/scotton/dev/projects/autocorp
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input scroll-area card avatar
```

### 4. Deploy to Amplify
```bash
npm install -g @aws-amplify/cli
amplify init
amplify add hosting
amplify publish
```

---

## File Structure

```
/home/scotton/dev/projects/autocorp/
├── PHASE5_AI_CHATBOX.md          # Full implementation guide (760 lines)
├── terraform/
│   └── modules/
│       ├── bedrock/              # Bedrock + Knowledge Base
│       ├── lambda-chat/          # Lambda + API Gateway
│       └── amplify/              # Amplify hosting
├── lambda/
│   ├── chat-handler/             # Chat processing logic
│   │   └── main.py
│   └── analytics-query/          # Athena query execution
│       └── main.py
└── frontend/                     # Next.js app
    ├── app/
    │   └── chat/
    │       └── page.tsx
    ├── components/
    │   └── chat/
    │       ├── ChatBox.tsx
    │       ├── MessageList.tsx
    │       └── InputBar.tsx
    └── lib/
        └── api-client.ts
```

---

## Cost Estimate

**Development Environment (Monthly):**
- Bedrock Nova Pro: $8-15
- OpenSearch Serverless: $140
- Lambda: $1-3
- API Gateway: $0.50
- Amplify Hosting: $0-15
- **Total: ~$150-180/month**

**Cost Optimization:**
- Use DynamoDB caching to reduce Bedrock calls
- Implement request throttling
- Use provisioned throughput for consistent traffic

---

## Timeline

### Week 1: Backend (5 days)
- Day 1: Bedrock setup
- Day 2: Knowledge base data prep
- Day 3: OpenSearch + Knowledge Base config
- Day 4: Lambda functions
- Day 5: API Gateway

### Week 2: Frontend (5 days)
- Day 6: Next.js setup
- Day 7: Chat UI components
- Day 8: API integration
- Day 9: Amplify deployment
- Day 10: Testing & polish

---

## Sample Use Cases

**Customer Support:**
```
User: "What parts are needed for an oil change?"
AI: "Based on our service catalog, an oil change requires:
     - 5 quarts of 5W-30 Motor Oil
     - 1 Oil Filter
     Total estimated cost: $70.00"
```

**Data Analytics:**
```
User: "What are our top-selling parts this month?"
AI: "Querying sales data... Top 3 parts:
     1. Brake Pads - 145 units
     2. Oil Filters - 132 units
     3. Air Filters - 98 units"
```

---

## Key Features

✅ **RAG-Enhanced Responses** - Grounded in actual AutoCorp data  
✅ **Real-Time Queries** - Direct Athena integration for analytics  
✅ **Mobile Responsive** - Works on all devices  
✅ **AWS Native** - Fully integrated with existing infrastructure  
✅ **Secure** - API keys + optional Cognito authentication  

---

## Testing Strategy

1. **Unit Tests** - Lambda functions, API client
2. **Integration Tests** - API → Lambda → Bedrock flow
3. **E2E Tests** - User sends message → receives response
4. **Load Tests** - 50-100 concurrent users

---

## Monitoring

**CloudWatch Dashboards:**
- API request count/errors
- Lambda execution duration
- Bedrock API latency
- Cost tracking

**Alarms:**
- Lambda error rate > 5%
- API Gateway 5xx errors
- Daily cost exceeds $20

---

## Next Steps

1. **Review full plan:** `PHASE5_AI_CHATBOX.md`
2. **Complete Phases 3-4** (DMS, DataSync, Athena)
3. **Request Bedrock access** in AWS Console
4. **Start Week 1:** Backend infrastructure

---

## Resources

- **Full Documentation:** `PHASE5_AI_CHATBOX.md` (760 lines)
- **Bedrock Docs:** https://docs.aws.amazon.com/bedrock/
- **Next.js Docs:** https://nextjs.org/docs
- **shadcn/ui:** https://ui.shadcn.com/

---

**Last Updated:** December 10, 2025  
**Author:** scotton

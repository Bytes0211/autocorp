# Phase 5: AI Chatbox with Amazon Bedrock & RAG

**Status:** Planning  
**Start Date:** TBD  
**Duration:** 8-10 days  
**Owner:** scotton

---

## Overview

Add an AI-powered chatbox using **Amazon Bedrock Nova Pro** with **Retrieval-Augmented Generation (RAG)** for customer support and data analytics queries. The solution leverages the existing AutoCorp data lake (1.19M orders, 400+ parts, 110 services) as the knowledge base.

### Key Features

- **Customer Support:** Answer questions about auto parts, services, and pricing
- **Data Analytics:** Query sales trends, inventory status, and customer insights
- **RAG Integration:** Ground responses in actual AutoCorp data from S3/Athena
- **AWS Native:** Fully integrated with existing AWS infrastructure

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Browser                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              AWS Amplify (Next.js Frontend)                      │
│  - React chatbox UI                                              │
│  - Tailwind CSS + shadcn/ui components                          │
│  - Authentication (Cognito)                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway (REST)                            │
│  - /chat/message (POST)                                          │
│  - /chat/history (GET)                                           │
│  - API Key authentication                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Lambda Functions                                │
│  - chat-handler: Process user queries                           │
│  - rag-retriever: Fetch relevant context                        │
│  - analytics-query: Execute Athena queries                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             Amazon Bedrock (Nova Pro)                            │
│  - Text generation                                               │
│  - Context-aware responses                                       │
│  - Streaming support                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            Amazon Bedrock Knowledge Base                         │
│  - Vector embeddings (Titan Embeddings G1)                      │
│  - OpenSearch Serverless (vector store)                         │
│  - Auto-sync from S3 data lake                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Existing Data Sources                               │
│  - S3 Data Lake (raw + curated zones)                           │
│  - AWS Athena (SQL queries)                                     │
│  - Glue Data Catalog                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Deployment:** AWS Amplify Hosting

### Backend
- **LLM:** Amazon Bedrock Nova Pro
- **RAG:** Bedrock Knowledge Bases + OpenSearch Serverless
- **API:** API Gateway REST
- **Compute:** Lambda (Python 3.12)
- **Auth:** Cognito User Pools (optional)

### Infrastructure
- **IaC:** Terraform (new modules)
- **Monitoring:** CloudWatch Logs + Metrics
- **Storage:** S3 (existing data lake)

---

## Implementation Plan

### Week 1: Backend Infrastructure (Days 1-5)

#### Day 1: Terraform Module - Bedrock Setup
**Tasks:**
- Create `terraform/modules/bedrock/` module
- Configure Bedrock model access (Nova Pro)
- Set up IAM roles for Lambda → Bedrock
- Request model access if needed

**Deliverables:**
- `terraform/modules/bedrock/main.tf`
- `terraform/modules/bedrock/variables.tf`
- `terraform/modules/bedrock/outputs.tf`

#### Day 2: Knowledge Base Preparation
**Tasks:**
- Create RAG data export script from Athena
- Format data for embeddings:
  - Auto parts catalog (400 items)
  - Service catalog (110 items)
  - Service-parts relationships (1,074 mappings)
  - Customer FAQs (synthetic/curated)
- Upload to S3 knowledge base bucket

**Deliverables:**
- `scripts/export_knowledge_base.py`
- S3 bucket: `s3://autocorp-dev-knowledge-base/`
- Formatted JSON/text documents ready for indexing

#### Day 3: Bedrock Knowledge Base Configuration
**Tasks:**
- Create OpenSearch Serverless collection (vector store)
- Configure Bedrock Knowledge Base
- Set up Titan Embeddings G1 for vectorization
- Test document ingestion and retrieval

**Deliverables:**
- OpenSearch Serverless collection operational
- Knowledge Base with 500+ documents indexed
- Test queries validated

#### Day 4: Lambda Functions
**Tasks:**
- Create `lambda/chat-handler/` function
  - Bedrock Nova Pro integration
  - RAG retrieval logic
  - Response streaming (optional)
- Create `lambda/analytics-query/` function
  - Athena query execution
  - Result formatting
- Deploy functions via Terraform

**Deliverables:**
- `lambda/chat-handler/main.py`
- `lambda/analytics-query/main.py`
- `terraform/modules/lambda-chat/main.tf`

#### Day 5: API Gateway Configuration
**Tasks:**
- Create REST API with endpoints:
  - `POST /chat/message` - Send user query
  - `GET /chat/history` - Retrieve chat history
  - `POST /analytics/query` - Execute analytics query
- Configure CORS for Amplify domain
- Set up API keys or Cognito authorization
- Test endpoints with Postman/curl

**Deliverables:**
- API Gateway deployed via Terraform
- API documentation (OpenAPI spec)
- Postman collection for testing

---

### Week 2: Frontend Development (Days 6-10)

#### Day 6: Next.js Project Setup
**Tasks:**
- Create Next.js app in `/frontend/` directory
- Initialize TypeScript + Tailwind CSS
- Install shadcn/ui components
- Set up project structure
- Configure environment variables

**Commands:**
```bash
cd /home/scotton/dev/projects/autocorp
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input scroll-area card avatar
```

**Deliverables:**
- `/frontend/` directory initialized
- Basic project structure
- Dependencies installed

#### Day 7: Chat UI Components
**Tasks:**
- Build `ChatBox` component
- Build `MessageList` component (user/AI messages)
- Build `InputBar` component (text input + send button)
- Build `ChatHeader` component
- Implement basic styling with Tailwind

**Deliverables:**
- `/frontend/components/chat/ChatBox.tsx`
- `/frontend/components/chat/MessageList.tsx`
- `/frontend/components/chat/InputBar.tsx`
- `/frontend/components/chat/ChatHeader.tsx`

#### Day 8: API Integration
**Tasks:**
- Create API client (`lib/api-client.ts`)
- Integrate with API Gateway endpoints
- Implement chat message sending
- Implement message history retrieval
- Add loading states and error handling

**Deliverables:**
- `/frontend/lib/api-client.ts`
- `/frontend/app/chat/page.tsx` (main chat interface)
- Working API → Frontend integration

#### Day 9: AWS Amplify Deployment
**Tasks:**
- Install Amplify CLI
- Initialize Amplify project
- Configure build settings
- Connect to Git repository
- Deploy to Amplify Hosting
- Configure custom domain (optional)

**Commands:**
```bash
npm install -g @aws-amplify/cli
amplify init
amplify add hosting
amplify publish
```

**Deliverables:**
- Amplify app deployed
- CI/CD pipeline from Git
- Public URL live

#### Day 10: Testing & Polish
**Tasks:**
- End-to-end testing (frontend → backend → Bedrock)
- UI/UX polish and refinements
- Mobile responsiveness testing
- Performance optimization
- Documentation updates

**Deliverables:**
- Fully functional chatbox
- Test results documented
- User guide created

---

## Terraform Module Structure

### New Modules

```
terraform/modules/
├── bedrock/
│   ├── main.tf                 # Bedrock model access
│   ├── knowledge_base.tf       # Knowledge Base config
│   ├── opensearch.tf           # OpenSearch Serverless
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
│
├── lambda-chat/
│   ├── main.tf                 # Lambda functions
│   ├── iam.tf                  # Execution roles
│   ├── api_gateway.tf          # REST API
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
│
└── amplify/
    ├── main.tf                 # Amplify app
    ├── iam.tf                  # Service role
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

### Root Module Updates

**`terraform/main.tf`:**
```hcl
# Add new modules
module "bedrock" {
  source = "./modules/bedrock"
  
  environment        = var.environment
  knowledge_base_bucket = module.s3.knowledge_base_bucket_id
}

module "lambda_chat" {
  source = "./modules/lambda-chat"
  
  environment           = var.environment
  bedrock_model_id      = module.bedrock.model_id
  knowledge_base_id     = module.bedrock.knowledge_base_id
  api_name              = "autocorp-chat-api"
}

module "amplify" {
  source = "./modules/amplify"
  
  environment      = var.environment
  repository_url   = var.github_repo_url
  api_gateway_url  = module.lambda_chat.api_gateway_url
}
```

---

## Lambda Function Examples

### chat-handler/main.py

```python
import json
import boto3
import os

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

KNOWLEDGE_BASE_ID = os.environ['KNOWLEDGE_BASE_ID']
MODEL_ID = 'us.amazon.nova-pro-v1:0'

def lambda_handler(event, context):
    """
    Handle chat messages with RAG-enhanced responses
    """
    body = json.loads(event['body'])
    user_message = body.get('message', '')
    
    # Step 1: Retrieve relevant context from Knowledge Base
    rag_response = bedrock_agent.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={'text': user_message},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 5
            }
        }
    )
    
    # Step 2: Build context from retrieval results
    context_docs = []
    for result in rag_response['retrievalResults']:
        context_docs.append(result['content']['text'])
    
    context = "\n\n".join(context_docs)
    
    # Step 3: Build prompt with context
    prompt = f"""You are an AI assistant for AutoCorp, an auto parts and service company.

Context from our knowledge base:
{context}

User question: {user_message}

Provide a helpful, accurate response based on the context above. If the context doesn't contain relevant information, say so."""
    
    # Step 4: Call Bedrock Nova Pro
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                'role': 'user',
                'content': [{'text': prompt}]
            }
        ],
        inferenceConfig={
            'maxTokens': 1000,
            'temperature': 0.7,
            'topP': 0.9
        }
    )
    
    # Step 5: Extract and return response
    ai_message = response['output']['message']['content'][0]['text']
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': ai_message,
            'sources': [doc[:100] + '...' for doc in context_docs[:3]]
        })
    }
```

---

## Frontend Component Examples

### ChatBox.tsx

```typescript
'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageList } from './MessageList';
import { InputBar } from './InputBar';
import { ChatHeader } from './ChatHeader';
import { apiClient } from '@/lib/api-client';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
}

export function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call API
      const response = await apiClient.sendMessage(content);
      
      // Add AI response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        sources: response.sources,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <ChatHeader />
      <MessageList messages={messages} isLoading={isLoading} />
      <div ref={messagesEndRef} />
      <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
```

### API Client (lib/api-client.ts)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || '';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface ChatResponse {
  message: string;
  sources?: string[];
}

export const apiClient = {
  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  },

  async getHistory(): Promise<Message[]> {
    const response = await fetch(`${API_BASE_URL}/chat/history`, {
      headers: {
        'x-api-key': API_KEY,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  },
};
```

---

## Knowledge Base Data Format

### Auto Parts Document Example

```json
{
  "id": "part-12345",
  "type": "auto_part",
  "sku": "BRK-PAD-001",
  "name": "Front Brake Pads - Ceramic",
  "category": "Brakes",
  "price": 89.99,
  "description": "High-performance ceramic brake pads for front wheels. Provides excellent stopping power with minimal dust. Compatible with most sedan and compact vehicles.",
  "metadata": {
    "stock_status": "in_stock",
    "popularity_rank": 15,
    "average_rating": 4.7
  }
}
```

### Service Document Example

```json
{
  "id": "service-48392017",
  "type": "service",
  "serviceid": "48392017",
  "name": "Oil Change Service",
  "category": "General Preventive Maintenance",
  "labor_cost": 45.00,
  "labor_minutes": 30,
  "description": "Complete oil change service including oil filter replacement, fluid top-off, and multi-point inspection.",
  "required_parts": [
    {"sku": "OIL-5W30-QT", "quantity": 5, "name": "5W-30 Motor Oil"},
    {"sku": "OIL-FILTER-STD", "quantity": 1, "name": "Oil Filter"}
  ],
  "estimated_total": 70.00
}
```

---

## Cost Estimates

### Development Environment (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| **Bedrock Nova Pro** | ~100K tokens/day | $8-15 |
| **Bedrock Knowledge Base** | 500 documents | $5 |
| **OpenSearch Serverless** | 2 OCUs | $140 |
| **Lambda** | 10K invocations/day | $1-3 |
| **API Gateway** | 10K requests/day | $0.50 |
| **Amplify Hosting** | 1 app, 5GB bandwidth | $0-15 |
| **CloudWatch Logs** | 5GB/month | $2.50 |
| **S3 (Knowledge Base)** | 1GB storage | $0.02 |

**Total: ~$157-181/month**

### Cost Optimization Strategies

1. **Use provisioned throughput** for OpenSearch if traffic is consistent
2. **Cache frequent queries** in DynamoDB (add $5/month, save on Bedrock calls)
3. **Use Lambda reserved concurrency** to control costs
4. **Implement request throttling** on API Gateway
5. **Use S3 Intelligent-Tiering** for knowledge base data

---

## Testing Strategy

### Unit Tests
- Lambda function logic
- API client functions
- React component rendering

### Integration Tests
- API Gateway → Lambda → Bedrock flow
- Knowledge Base retrieval accuracy
- Frontend → API integration

### End-to-End Tests
- User sends message → receives response
- RAG context relevance validation
- Analytics query execution

### Load Tests
- Concurrent user simulation (50-100 users)
- API Gateway throttling validation
- Lambda cold start optimization

---

## Monitoring & Observability

### CloudWatch Dashboards

**Chat Performance Dashboard:**
- API Gateway request count/errors
- Lambda execution duration (p50, p99)
- Bedrock API latency
- Knowledge Base retrieval time

**Cost Dashboard:**
- Bedrock token usage
- Lambda invocation count
- OpenSearch OCU hours
- API Gateway requests

### Alarms

- Lambda error rate > 5%
- API Gateway 5xx errors > 10/min
- Bedrock throttling detected
- Daily cost exceeds $20

---

## Security Considerations

1. **API Authentication**
   - Use API keys for development
   - Migrate to Cognito User Pools for production
   - Implement rate limiting (100 req/min per user)

2. **Data Privacy**
   - No PII in chat logs
   - Encrypt chat history (DynamoDB encryption at rest)
   - Implement session expiration (24 hours)

3. **IAM Least Privilege**
   - Lambda execution role: Bedrock + Knowledge Base only
   - No direct S3 access from Lambda
   - VPC endpoints for private communication

4. **Input Validation**
   - Sanitize user input (max 500 chars)
   - Rate limiting on API Gateway
   - SQL injection prevention (parameterized Athena queries)

---

## Success Criteria

### Technical Metrics
- ✅ Chat response time < 3 seconds (p95)
- ✅ RAG retrieval accuracy > 85%
- ✅ API Gateway availability > 99.9%
- ✅ Lambda cold start < 1 second
- ✅ Frontend load time < 2 seconds

### User Experience Metrics
- ✅ Message delivery success rate > 99%
- ✅ Relevant responses (manual evaluation)
- ✅ Mobile-responsive UI
- ✅ Intuitive chat interface

### Cost Metrics
- ✅ Monthly cost < $200 (dev environment)
- ✅ Cost per conversation < $0.10

---

## Deployment Checklist

### Phase 1: Backend (Week 1)
- [ ] Request Bedrock Nova Pro model access
- [ ] Create Terraform modules (bedrock, lambda-chat)
- [ ] Export knowledge base data from Athena
- [ ] Deploy OpenSearch Serverless collection
- [ ] Configure Bedrock Knowledge Base
- [ ] Deploy Lambda functions
- [ ] Create API Gateway REST API
- [ ] Test API endpoints with Postman

### Phase 2: Frontend (Week 2)
- [ ] Initialize Next.js project
- [ ] Build chat UI components
- [ ] Integrate API client
- [ ] Deploy to AWS Amplify
- [ ] Configure custom domain (optional)
- [ ] End-to-end testing
- [ ] Update documentation

### Phase 3: Production Readiness
- [ ] Add Cognito authentication
- [ ] Implement chat history persistence (DynamoDB)
- [ ] Set up CloudWatch alarms
- [ ] Create operational runbook
- [ ] Load testing
- [ ] Security review
- [ ] User acceptance testing

---

## References

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock Knowledge Bases Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Nova Pro Model Card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-nova.html)
- [AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html)
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)

---

## Next Steps

1. **Request Bedrock Model Access** (if not already available)
2. **Review and approve this plan**
3. **Create project timeline** (8-10 days)
4. **Begin Phase 1: Backend Infrastructure**

---

**Document Version:** 1.0  
**Last Updated:** December 10, 2025  
**Author:** scotton

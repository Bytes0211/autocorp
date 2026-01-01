# AutoCorp AI Chatbox - Frontend Implementation Guide

**Status:** Infrastructure Ready (Lambda + API Gateway Operational)  
**Next Steps:** Complete React Components Implementation

---

## Current Status

### ✅ Completed (Days 4-5)
- Lambda functions deployed and operational
  - `autocorp-chat-handler-dev`: Bedrock RAG with Nova Pro
  - `autocorp-analytics-query-dev`: Athena query execution
- API Gateway REST API deployed
  - Base URL: `https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev`
  - Chat endpoint: `/chat`
  - Analytics endpoint: `/analytics`
- API key secured in Secrets Manager
- CORS configured for web access
- Verified working chat endpoint with test query

### 📝 Pending (Days 6-7)
- Install Node.js dependencies
- Implement React components
- Configure environment variables
- Deploy to AWS Amplify

---

## Quick Start

### 1. Install Dependencies
```bash
cd /home/scotton/dev/projects/autocorp/frontend/autocorp-chatbox
npm install
```

### 2. Configure Environment Variables
Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev
NEXT_PUBLIC_API_KEY=nWU3TtU4G88fmNm0VDLyBONFlvx6gwE6WZGRTEY7
```

### 3. Run Development Server
```bash
npm run dev
```

Access at `http://localhost:3000`

---

## API Testing

### Test Chat Endpoint
```bash
curl -X POST "https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: nWU3TtU4G88fmNm0VDLyBONFlvx6gwE6WZGRTEY7" \
  -d '{"message": "What parts are needed for an oil change?"}'
```

**Example Response:**
```json
{
  "message": "Based on the provided context, the following parts are needed for an oil change...",
  "sources": [
    {
      "uri": "s3://autocorp-datalake-dev/knowledge-base/service_parts.json",
      "relevance_score": 0.576
    }
  ],
  "metadata": {
    "knowledge_base_results": 5,
    "model": "amazon.nova-pro-v1:0"
  }
}
```

### Test Analytics Endpoint
```bash
curl -X POST "https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev/analytics" \
  -H "Content-Type: application/json" \
  -H "x-api-key: nWU3TtU4G88fmNm0VDLyBONFlvx6gwE6WZGRTEY7" \
  -d '{"query_name": "sales_summary"}'
```

---

## Component Architecture

### Required Components

#### 1. `app/page.tsx` (Main Page)
```typescript
import ChatBox from '@/components/ChatBox';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto py-8">
        <ChatBox />
      </div>
    </main>
  );
}
```

#### 2. `components/ChatBox.tsx` (Main Container)
```typescript
'use client';

import { useState } from 'react';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import InputBar from './InputBar';
import { sendMessage } from '@/lib/api-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ uri: string; relevance_score: number }>;
  timestamp: Date;
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendMessage(text);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        sources: response.sources,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Handle error state
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-xl h-[700px] flex flex-col">
      <ChatHeader />
      <MessageList messages={messages} />
      <InputBar onSendMessage={handleSendMessage} loading={loading} />
    </div>
  );
}
```

#### 3. `components/ChatHeader.tsx`
```typescript
export default function ChatHeader() {
  return (
    <div className="bg-indigo-600 text-white p-4 rounded-t-lg">
      <h1 className="text-2xl font-bold">AutoCorp AI Assistant</h1>
      <p className="text-sm text-indigo-100">
        Ask me about auto parts, services, and more!
      </p>
    </div>
  );
}
```

#### 4. `components/MessageList.tsx`
```typescript
import { useEffect, useRef } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ uri: string; relevance_score: number }>;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="text-center text-gray-500 mt-20">
          <p className="text-lg">Welcome to AutoCorp AI Assistant!</p>
          <p className="text-sm mt-2">
            Ask me anything about auto parts and services.
          </p>
        </div>
      ) : (
        messages.map(message => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 text-xs opacity-75">
                  <p className="font-semibold">Sources:</p>
                  {message.sources.map((source, idx) => (
                    <p key={idx}>• Score: {source.relevance_score}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
```

#### 5. `components/InputBar.tsx`
```typescript
'use client';

import { useState, FormEvent } from 'react';

interface InputBarProps {
  onSendMessage: (message: string) => void;
  loading: boolean;
}

export default function InputBar({ onSendMessage, loading }: InputBarProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about auto parts or services..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </form>
  );
}
```

#### 6. `lib/api-client.ts`
```typescript
interface ChatResponse {
  message: string;
  sources: Array<{
    uri: string;
    relevance_score: number;
  }>;
  metadata: {
    knowledge_base_results: number;
    model: string;
  };
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.NEXT_PUBLIC_API_KEY!
    },
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to send message');
  }

  return response.json();
}
```

---

## Deployment to AWS Amplify

### Option 1: Amplify Console (Recommended)
1. Push code to GitHub
2. Connect repository in Amplify Console
3. Configure build settings:
   ```yaml
   version: 1
   applications:
     - frontend:
         phases:
           preBuild:
             commands:
               - cd frontend/autocorp-chatbox
               - npm ci
           build:
             commands:
               - npm run build
         artifacts:
           baseDirectory: .next
           files:
             - '**/*'
         cache:
           paths:
             - node_modules/**/*
   ```
4. Add environment variables in Amplify Console
5. Deploy

### Option 2: Amplify CLI
```bash
npm install -g @aws-amplify/cli
amplify init
amplify add hosting
amplify publish
```

---

## Known Issues & TODOs

### Lambda/API Gateway Issues
1. **Analytics Lambda Glue Permissions**: Analytics endpoint returns 403 when querying Athena
   - **Fix**: Add `glue:GetDatabase` permission to analytics Lambda IAM role
   - **Impact**: Analytics queries currently fail

### Frontend TODOs
1. Install dependencies (`npm install`)
2. Create all component files listed above
3. Test locally with dev server
4. Configure production environment variables
5. Deploy to Amplify
6. Set up custom domain (optional)
7. Add error boundaries and loading states
8. Add analytics tracking
9. Add mobile responsiveness testing
10. Add unit tests

---

## Performance Targets

- **Chat Response Time:** < 3 seconds (p95)
- **Page Load Time:** < 2 seconds
- **RAG Retrieval Accuracy:** > 85%
- **API Gateway Availability:** > 99.9%

---

## Security Notes

- API key stored in Secrets Manager
- CORS configured for specific origins in production
- Rate limiting: 100 requests/minute
- Usage quota: 10,000 requests/month

---

## Cost Estimates

**Dev Environment (per month):**
- OpenSearch Serverless: ~$140
- Lambda invocations: ~$5
- API Gateway: ~$3
- **Total:** ~$148/month

---

## Next Steps

1. ✅ Lambda functions operational (chat endpoint verified)
2. ⚠️ Fix analytics Lambda Glue permissions
3. 📝 Complete frontend component implementation
4. 📝 Deploy to Amplify
5. 📝 End-to-end testing
6. 📝 Documentation updates

---

**Last Updated:** January 1, 2026  
**Infrastructure Status:** Operational  
**Frontend Status:** Scaffolded, pending component implementation

const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT || '';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface ChatResponse {
  message: string;
  sources?: Array<{
    uri: string;
    relevance_score: number;
  }>;
  metadata?: {
    knowledge_base_results: number;
    model: string;
  };
}

export interface AnalyticsResponse {
  data: Array<Record<string, string>>;
  metadata: {
    execution_id: string;
    database: string;
    query_source: string;
    row_count: number;
  };
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_ENDPOINT}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY,
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to send message');
  }

  return response.json();
}

export async function getAnalytics(queryName: string): Promise<AnalyticsResponse> {
  const response = await fetch(`${API_ENDPOINT}/analytics`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY,
    },
    body: JSON.stringify({ query_name: queryName }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch analytics');
  }

  return response.json();
}

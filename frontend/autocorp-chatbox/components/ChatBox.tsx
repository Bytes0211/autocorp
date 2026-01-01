'use client';

import { useState } from 'react';
import { sendChatMessage, ChatResponse } from '@/lib/api-client';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import InputBar from './InputBar';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  sources?: Array<{
    uri: string;
    relevance_score: number;
  }>;
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello I\'m Mici, your AutoCorp AI assistant. How can I help you with questions about auto parts, services, and pricing?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Call API
      const response: ChatResponse = await sendChatMessage(text);

      // Add bot response
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.message,
        sender: 'bot',
        timestamp: new Date(),
        sources: response.sources,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto bg-white shadow-2xl">
      <ChatHeader />
      <MessageList messages={messages} isLoading={isLoading} />
      <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
      {error && (
        <div className="px-6 py-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm">
          <span className="font-semibold">Error:</span> {error}
        </div>
      )}
    </div>
  );
}

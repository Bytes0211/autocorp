'use client';

import { useEffect, useRef } from 'react';
import { Message } from './ChatBox';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex items-end space-x-2 ${
            message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
          }`}
        >
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm ${
            message.sender === 'user' ? 'bg-gray-500' : 'bg-blue-600'
          }`}>
            {message.sender === 'user' ? 'U' : 'M'}
          </div>
          
          {/* Message Bubble */}
          <div className="flex flex-col max-w-xs md:max-w-md lg:max-w-lg">
            <div
              className={`px-4 py-3 rounded-2xl shadow-sm ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 rounded-bl-none'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200 text-xs opacity-80">
                  <p className="font-semibold mb-1">📚 Sources:</p>
                  {message.sources.map((source, idx) => (
                    <p key={idx} className="truncate">
                      • {source.uri.split('/').pop()} ({(source.relevance_score * 100).toFixed(0)}% match)
                    </p>
                  ))}
                </div>
              )}
            </div>
            <p className={`text-xs mt-1 px-2 ${
              message.sender === 'user' ? 'text-right' : 'text-left'
            } text-gray-500`}>
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          </div>
        </div>
      ))}
      {isLoading && (
        <div className="flex items-end space-x-2">
          {/* Mici Avatar */}
          <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm bg-blue-600">
            M
          </div>
          
          {/* Typing Indicator */}
          <div className="bg-white text-gray-800 shadow-sm px-4 py-3 rounded-2xl rounded-bl-none">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

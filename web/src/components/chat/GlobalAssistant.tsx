'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import ChatPanel from './ChatPanel';

interface GlobalAssistantProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function GlobalAssistant({ isOpen, onClose }: GlobalAssistantProps) {
  const [context, setContext] = useState<{
    workflows_count: number;
    executions_count: number;
    user_name: string;
    business_type?: string;
  } | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadContext();
    }
  }, [isOpen]);

  const loadContext = async () => {
    try {
      const data = await api.getAssistantContext();
      setContext(data.context_summary);
    } catch (error) {
      console.error('Failed to load context:', error);
    }
  };

  const handleSendMessage = async (message: string, history: Array<{role: string, content: string}>) => {
    const result = await api.chatAssistant(message, history);
    return result.response;
  };

  if (!isOpen) return null;

  const welcomeMessage = context 
    ? `Hi${context.user_name ? `, ${context.user_name.split(' ')[0]}` : ''}! 👋\n\nI'm your Aivaro AI assistant. I have access to your ${context.workflows_count} workflow${context.workflows_count !== 1 ? 's' : ''} and ${context.executions_count} execution${context.executions_count !== 1 ? 's' : ''}.\n\nHow can I help you today?`
    : "Hi! 👋 I'm your Aivaro AI assistant. I can help you with your workflows, analyze results, and suggest improvements. What would you like to know?";

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Only close if clicking the backdrop itself, not the modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="w-full max-w-lg animate-in fade-in slide-in-from-bottom-4 duration-300" onClick={(e) => e.stopPropagation()}>
        <div className="relative">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute -top-2 -right-2 z-10 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-100 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <ChatPanel
            title="Aivaro AI Assistant"
            placeholder="Ask me anything about your workflows..."
            welcomeMessage={welcomeMessage}
            onSendMessage={handleSendMessage}
            className="shadow-2xl"
          />

          {/* Context info */}
          {context && (
            <div className="mt-2 px-4 py-2 bg-gray-50 rounded-lg text-xs text-gray-500 flex items-center justify-center gap-4">
              <span>📊 {context.workflows_count} workflows</span>
              <span>⚡ {context.executions_count} executions</span>
              {context.business_type && <span>🏢 {context.business_type}</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { X, Sparkles, Workflow, Zap, Building2 } from 'lucide-react';
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

  const welcomeMessage = context 
    ? `Hi${context.user_name ? `, ${context.user_name.split(' ')[0]}` : ''}!\n\nI'm your Aivaro AI assistant. I can help you with your ${context.workflows_count} workflow${context.workflows_count !== 1 ? 's' : ''} and analyze your ${context.executions_count} execution${context.executions_count !== 1 ? 's' : ''}.\n\nHow can I help you today?`
    : "Hi! I'm your Aivaro AI assistant. I can help you with your workflows, analyze results, and suggest improvements. What would you like to know?";

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />
      
      {/* Slide-in Panel */}
      <div 
        className={`fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col transform transition-transform duration-300 ease-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-primary-50 to-purple-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">AI Assistant</h2>
              <p className="text-xs text-gray-500">Powered by Aivaro</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Context Stats */}
        {context && (
          <div className="px-6 py-3 bg-gray-50 border-b border-gray-100 flex items-center gap-4 text-xs text-gray-600">
            <span className="flex items-center gap-1">
              <Workflow className="w-3.5 h-3.5" />
              {context.workflows_count} workflows
            </span>
            <span className="flex items-center gap-1">
              <Zap className="w-3.5 h-3.5" />
              {context.executions_count} executions
            </span>
            {context.business_type && (
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5" />
                {context.business_type}
              </span>
            )}
          </div>
        )}

        {/* Chat Panel */}
        <div className="flex-1 overflow-hidden">
          <ChatPanel
            title=""
            placeholder="Ask me anything about your workflows..."
            welcomeMessage={welcomeMessage}
            onSendMessage={handleSendMessage}
            className="h-full border-0 rounded-none shadow-none"
          />
        </div>
      </div>
    </>
  );
}

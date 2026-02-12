'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Bot, AlertCircle, Package } from 'lucide-react';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Execution } from '@/types';
import ChatPanel from '@/components/chat/ChatPanel';

export default function ExecutionDetailPage() {
  const params = useParams();
  const [execution, setExecution] = useState<Execution | null>(null);
  const [loading, setLoading] = useState(true);
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    if (params.id) {
      loadExecution(params.id as string);
    }
  }, [params.id]);

  const loadExecution = async (id: string) => {
    try {
      const data = await api.getExecution(id);
      // Map API response to frontend types
      const execution = {
        ...data,
        node_executions: (data.execution_nodes || data.node_executions || []).map((n: any) => ({
          ...n,
          output: n.output_data || n.output,
          input: n.input_data || n.input,
        })),
      };
      setExecution(execution);
      // Auto-show chat if execution is completed with output
      if (execution.status === 'completed' && execution.node_executions?.some((n: any) => n.output)) {
        setShowChat(true);
      }
    } catch (err) {
      console.error('Failed to load execution:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChatMessage = async (message: string, history: Array<{role: string, content: string}>) => {
    if (!execution) throw new Error('No execution loaded');
    const result = await api.chatExecution(execution.id, message, history);
    return result.response;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'running':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'skipped':
        return 'bg-gray-100 text-gray-600 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!execution) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold mb-2">Execution not found</h2>
        <Link href="/app/executions" className="text-primary-600 hover:underline">
          Back to Run History
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/app/executions"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          ← Back to Run History
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold">Execution Details</h1>
            <p className="text-sm text-gray-500">ID: {execution.id}</p>
          </div>
          <div className="flex items-center gap-3">
            {execution.is_test && (
              <span className="px-3 py-1.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-700 border border-yellow-200">
                🧪 Test Run
              </span>
            )}
            <span
              className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(
                execution.status
              )}`}
            >
              {execution.status.replace('_', ' ')}
            </span>
          </div>
        </div>
        {execution.is_test && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
            ⚠️ <strong>Test Mode:</strong> No real actions were performed. Emails were not sent, sheets were not accessed, and AI responses were simulated.
          </div>
        )}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Started</div>
            <div className="font-medium">{formatDate(execution.started_at)}</div>
          </div>
          {execution.completed_at && (
            <div>
              <div className="text-gray-500">Completed</div>
              <div className="font-medium">{formatDate(execution.completed_at)}</div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold mb-6">Step Timeline</h2>
          <div className="space-y-4">
            {execution.node_executions && execution.node_executions.length > 0 ? (
              execution.node_executions.map((node, index) => (
                <div
                  key={node.id}
                  className={`relative pl-8 pb-4 ${
                    index !== execution.node_executions!.length - 1
                      ? 'border-l-2 border-gray-200'
                      : ''
                  }`}
                >
                  <div
                    className={`absolute left-0 -translate-x-1/2 w-4 h-4 rounded-full border-2 ${getStatusColor(
                      node.status
                    )}`}
                  />
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-medium">{node.node_label || node.node_type}</div>
                        <div className="text-xs text-gray-400">{node.node_type}</div>
                      </div>
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${getStatusColor(
                          node.status
                        )}`}
                      >
                        {node.status}
                      </span>
                    </div>
                    {node.started_at && (
                      <div className="text-xs text-gray-500 mb-2">
                        {formatDate(node.started_at)}
                        {node.duration_ms && ` • ${node.duration_ms}ms`}
                      </div>
                    )}
                    
                    {/* Logs - Always show if present */}
                    {node.logs && (
                      <div className="mt-3 p-3 bg-gray-800 text-gray-100 rounded text-xs font-mono whitespace-pre-wrap overflow-x-auto">
                        {node.logs}
                      </div>
                    )}
                    
                    {/* Output - Collapsible */}
                    {node.output && Object.keys(node.output).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800 flex items-center gap-1">
                          <Package className="w-3 h-3" /> View Output Data
                        </summary>
                        <pre className="mt-2 p-3 bg-white rounded border text-xs overflow-x-auto max-h-64 overflow-y-auto">
                          {JSON.stringify(node.output, null, 2)}
                        </pre>
                      </details>
                    )}
                    
                    {/* Error */}
                    {node.error && (
                      <div className="mt-2 p-3 bg-red-50 text-red-700 rounded text-sm flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" /> {node.error}
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No steps executed yet.</p>
            )}
          </div>
        </div>

        {/* AI Chat Panel */}
        <div className="lg:col-span-1">
          {showChat ? (
            <ChatPanel
              title="Ask About Results"
              placeholder="Ask about this execution..."
              welcomeMessage={`I've analyzed this ${execution.status === 'completed' ? 'completed' : execution.status} workflow run. What would you like to know about the results?`}
              onSendMessage={handleChatMessage}
            />
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Bot className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI Assistant</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Ask questions about this workflow run and its results
                </p>
                <button
                  onClick={() => setShowChat(true)}
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm"
                >
                  Start Chat
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

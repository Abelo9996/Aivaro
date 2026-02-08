'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Execution } from '@/types';

export default function ExecutionDetailPage() {
  const params = useParams();
  const [execution, setExecution] = useState<Execution | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadExecution(params.id as string);
    }
  }, [params.id]);

  const loadExecution = async (id: string) => {
    try {
      const data = await api.getExecution(id);
      setExecution(data);
    } catch (err) {
      console.error('Failed to load execution:', err);
    } finally {
      setLoading(false);
    }
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
          <span
            className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(
              execution.status
            )}`}
          >
            {execution.status.replace('_', ' ')}
          </span>
        </div>
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
          <div>
            <div className="text-gray-500">Test Run</div>
            <div className="font-medium">{execution.is_test ? 'Yes' : 'No'}</div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
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
                    <div className="font-medium">{node.node_id}</div>
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
                    </div>
                  )}
                  {node.output && (
                    <details className="mt-2">
                      <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800">
                        View Output
                      </summary>
                      <pre className="mt-2 p-3 bg-white rounded border text-xs overflow-x-auto">
                        {JSON.stringify(node.output, null, 2)}
                      </pre>
                    </details>
                  )}
                  {node.error && (
                    <div className="mt-2 p-3 bg-red-50 text-red-700 rounded text-sm">
                      {node.error}
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
    </div>
  );
}

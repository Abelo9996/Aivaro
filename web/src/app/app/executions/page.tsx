'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Execution } from '@/types';

export default function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExecutions();
  }, []);

  const loadExecutions = async () => {
    try {
      const data = await api.getExecutions();
      setExecutions(data);
    } catch (err) {
      console.error('Failed to load executions:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      case 'running':
        return 'bg-blue-100 text-blue-700';
      case 'pending_approval':
        return 'bg-amber-100 text-amber-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      case 'running':
        return '⏳';
      case 'pending_approval':
        return '⏸️';
      default:
        return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading run history...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Run History</h1>
        <p className="text-gray-500">See what your workflows have been doing</p>
      </div>

      {executions.length === 0 ? (
        <div 
          data-walkthrough="executions-list"
          className="bg-white rounded-xl border border-gray-200 p-12 text-center"
        >
          <div className="text-5xl mb-4">📊</div>
          <h3 className="text-lg font-semibold mb-2">No runs yet</h3>
          <p className="text-gray-500 mb-6">
            Once your workflows start running, you'll see them here.
          </p>
          <Link
            href="/app/workflows"
            className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700"
          >
            View Workflows
          </Link>
        </div>
      ) : (
        <div data-walkthrough="executions-list" className="space-y-4">
          {executions.map((execution) => (
            <Link
              key={execution.id}
              href={`/app/executions/${execution.id}`}
              className="block bg-white rounded-xl border border-gray-200 p-4 hover:border-primary-300 hover:shadow-sm transition"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-2xl">{getStatusIcon(execution.status)}</span>
                  <div>
                    <div className="font-medium">
                      {execution.workflow_id}
                    </div>
                    <div className="text-sm text-gray-500">
                      Started {formatDate(execution.started_at)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span
                    className={`px-3 py-1 text-xs rounded-full ${getStatusColor(
                      execution.status
                    )}`}
                  >
                    {execution.status.replace('_', ' ')}
                  </span>
                  <span className="text-gray-400">→</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

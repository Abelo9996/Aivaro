'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Workflow } from '@/types';

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      const data = await api.getWorkflows();
      setWorkflows(data);
    } catch (err) {
      console.error('Failed to load workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this workflow?')) return;
    
    try {
      await api.deleteWorkflow(id);
      setWorkflows(workflows.filter(w => w.id !== id));
    } catch (err) {
      console.error('Failed to delete workflow:', err);
    }
  };

  const handleToggleActive = async (workflow: Workflow, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      const updated = await api.updateWorkflow(workflow.id, {
        is_active: !workflow.is_active,
      });
      setWorkflows(workflows.map(w => w.id === updated.id ? updated : w));
    } catch (err) {
      console.error('Failed to toggle workflow:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading workflows...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-500">Manage your automations</p>
        </div>
        <Link
          href="/app/workflows/new"
          className="bg-primary-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-primary-700"
        >
          + New Workflow
        </Link>
      </div>

      {workflows.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="text-5xl mb-4">⚡</div>
          <h3 className="text-lg font-semibold mb-2">No workflows yet</h3>
          <p className="text-gray-500 mb-6">
            Create your first automation to start saving time.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/app/templates"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700"
            >
              Browse Templates
            </Link>
            <Link
              href="/app/workflows/new"
              className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200"
            >
              Create from Scratch
            </Link>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">
                  Name
                </th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">
                  Steps
                </th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">
                  Status
                </th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">
                  Updated
                </th>
                <th className="text-right px-6 py-3 text-sm font-medium text-gray-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {workflows.map((workflow) => (
                <tr key={workflow.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link
                      href={`/app/workflows/${workflow.id}`}
                      className="font-medium text-gray-900 hover:text-primary-600"
                    >
                      {workflow.name}
                    </Link>
                    {workflow.description && (
                      <p className="text-sm text-gray-500 truncate max-w-xs">
                        {workflow.description}
                      </p>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {workflow.nodes.length} steps
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={(e) => handleToggleActive(workflow, e)}
                      className={`px-3 py-1 text-xs rounded-full ${
                        workflow.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {workflow.is_active ? 'Active' : 'Draft'}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(workflow.updated_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={(e) => handleDelete(workflow.id, e)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

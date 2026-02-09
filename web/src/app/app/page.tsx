'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Workflow, Approval } from '@/types';

export default function DashboardPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [workflowsData, approvalsData] = await Promise.all([
        api.getWorkflows(),
        api.getApprovals('pending'),
      ]);
      setWorkflows(workflowsData);
      setApprovals(approvalsData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8" data-walkthrough="dashboard">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Welcome back! Here's what's happening.</p>
      </div>

      {/* Pending Approvals */}
      {approvals.length > 0 && (
        <div className="mb-8">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">⏳</span>
              <div>
                <h2 className="font-semibold text-amber-900">
                  {approvals.length} action{approvals.length !== 1 ? 's' : ''} waiting for your approval
                </h2>
                <p className="text-sm text-amber-700">
                  Review these before they can proceed.
                </p>
              </div>
            </div>
            <Link
              href="/app/approvals"
              className="inline-block bg-amber-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-amber-700"
            >
              Review Approvals
            </Link>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Link
          href="/app/workflows/new"
          data-walkthrough="quick-action-create"
          className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-sm transition"
        >
          <div className="text-3xl mb-3">✨</div>
          <h3 className="font-semibold mb-1">Create Workflow</h3>
          <p className="text-sm text-gray-500">Build a new automation</p>
        </Link>
        <Link
          href="/app/templates"
          data-walkthrough="quick-action-templates"
          className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-sm transition"
        >
          <div className="text-3xl mb-3">📋</div>
          <h3 className="font-semibold mb-1">Browse Templates</h3>
          <p className="text-sm text-gray-500">Start from a template</p>
        </Link>
        <Link
          href="/app/executions"
          data-walkthrough="quick-action-history"
          className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-sm transition"
        >
          <div className="text-3xl mb-3">📊</div>
          <h3 className="font-semibold mb-1">Run History</h3>
          <p className="text-sm text-gray-500">See what's happened</p>
        </Link>
      </div>

      {/* Workflows */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Your Workflows</h2>
          <Link
            href="/app/workflows"
            className="text-sm text-primary-600 hover:underline"
          >
            View all
          </Link>
        </div>

        {workflows.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="text-5xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold mb-2">No workflows yet</h3>
            <p className="text-gray-500 mb-6">
              Create your first automation to get started.
            </p>
            <Link
              href="/app/templates"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700"
            >
              Browse Templates
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 divide-y">
            {workflows.slice(0, 5).map((workflow) => (
              <Link
                key={workflow.id}
                href={`/app/workflows/${workflow.id}`}
                className="block p-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{workflow.name}</div>
                    <div className="text-sm text-gray-500">
                      {workflow.nodes.length} steps • Updated {formatDate(workflow.updated_at)}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        workflow.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {workflow.is_active ? 'Active' : 'Draft'}
                    </span>
                    <span className="text-gray-400">→</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

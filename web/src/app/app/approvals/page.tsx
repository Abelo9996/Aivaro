'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Approval } from '@/types';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'pending' | 'approved' | 'rejected' | 'all'>('pending');

  useEffect(() => {
    loadApprovals();
  }, [filter]);

  const loadApprovals = async () => {
    try {
      const data = await api.getApprovals(filter === 'all' ? undefined : filter);
      setApprovals(data);
    } catch (err) {
      console.error('Failed to load approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await api.approveAction(id);
      loadApprovals();
    } catch (err) {
      console.error('Failed to approve:', err);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await api.rejectAction(id);
      loadApprovals();
    } catch (err) {
      console.error('Failed to reject:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading approvals...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Approvals</h1>
        <p className="text-gray-500">
          Review actions that need your permission before running
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        {(['pending', 'approved', 'rejected', 'all'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === status
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {approvals.length === 0 ? (
        <div 
          data-walkthrough="approvals-list"
          className="bg-white rounded-xl border border-gray-200 p-12 text-center"
        >
          <div className="text-5xl mb-4">✅</div>
          <h3 className="text-lg font-semibold mb-2">
            {filter === 'pending' ? 'All caught up!' : 'No approvals found'}
          </h3>
          <p className="text-gray-500">
            {filter === 'pending'
              ? "You don't have any pending approvals right now."
              : `No ${filter} approvals to show.`}
          </p>
        </div>
      ) : (
        <div data-walkthrough="approvals-list" className="space-y-4">
          {approvals.map((approval) => (
            <div
              key={approval.id}
              className="bg-white rounded-xl border border-gray-200 p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">
                      {approval.status === 'pending'
                        ? '⏳'
                        : approval.status === 'approved'
                        ? '✅'
                        : '❌'}
                    </span>
                    <span className="font-semibold">{approval.node_type}</span>
                    <span
                      className={`px-2 py-0.5 text-xs rounded-full ${
                        approval.status === 'pending'
                          ? 'bg-amber-100 text-amber-700'
                          : approval.status === 'approved'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {approval.status}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3">{approval.message}</p>
                  <div className="text-sm text-gray-500">
                    Requested {formatDate(approval.created_at)}
                  </div>
                  {approval.action_data && (
                    <details className="mt-3">
                      <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800">
                        View Action Details
                      </summary>
                      <pre className="mt-2 p-3 bg-gray-50 rounded-lg text-xs overflow-x-auto">
                        {JSON.stringify(approval.action_data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
                {approval.status === 'pending' && (
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleReject(approval.id)}
                      className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => handleApprove(approval.id)}
                      className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700"
                    >
                      Approve
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 mb-2">
          💡 About Approvals
        </h3>
        <p className="text-sm text-blue-700">
          Some actions in your workflows require your approval before they run.
          This protects you from accidentally sending emails, making payments,
          or taking other important actions. You can configure which steps need
          approval in the workflow editor.
        </p>
      </div>
    </div>
  );
}

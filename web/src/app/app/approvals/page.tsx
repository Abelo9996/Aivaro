'use client';

import { useEffect, useState } from 'react';
import { Info, Mail, CreditCard, Phone, MessageSquare, Calendar, FileText } from 'lucide-react';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Approval } from '@/types';

function ActionIcon({ type }: { type?: string }) {
  const cls = "w-5 h-5";
  switch (type) {
    case 'email': return <Mail className={cls} />;
    case 'payment_link':
    case 'invoice': return <CreditCard className={cls} />;
    case 'sms':
    case 'whatsapp': return <MessageSquare className={cls} />;
    case 'phone_call': return <Phone className={cls} />;
    case 'calendar_event': return <Calendar className={cls} />;
    default: return <FileText className={cls} />;
  }
}

function ActionPreview({ data }: { data: Record<string, any> }) {
  if (!data || !data.type) return null;

  switch (data.type) {
    case 'email':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">To:</span> {data.to}</div>
          <div><span className="font-medium text-gray-700">Subject:</span> {data.subject}</div>
          {data.body_preview && (
            <div className="mt-2 p-3 bg-white rounded border text-gray-600 whitespace-pre-wrap text-xs">
              {data.body_preview}
            </div>
          )}
        </div>
      );
    case 'payment_link':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">Amount:</span> ${data.amount}</div>
          <div><span className="font-medium text-gray-700">Product:</span> {data.product_name}</div>
        </div>
      );
    case 'invoice':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">Customer:</span> {data.customer_email}</div>
          <div><span className="font-medium text-gray-700">Amount:</span> ${data.amount}</div>
          <div><span className="font-medium text-gray-700">Description:</span> {data.description}</div>
          <div><span className="font-medium text-gray-700">Due:</span> {data.due_days} days</div>
          {data.auto_send === 'true' && (
            <div className="text-amber-600 font-medium">⚠️ Invoice will be auto-sent to customer</div>
          )}
        </div>
      );
    case 'sms':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">To:</span> {data.to}</div>
          <div className="p-3 bg-white rounded border text-gray-600">{data.body}</div>
        </div>
      );
    case 'whatsapp':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">To:</span> {data.to}</div>
          <div className="p-3 bg-white rounded border text-gray-600">{data.body}</div>
          {data.media_url && <div><span className="font-medium text-gray-700">Attachment:</span> {data.media_url}</div>}
        </div>
      );
    case 'phone_call':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">To:</span> {data.to}</div>
          <div className="p-3 bg-white rounded border text-gray-600">{data.message}</div>
          <div className="text-gray-500 text-xs italic">{data.note}</div>
        </div>
      );
    case 'email_campaign':
      return (
        <div className="mt-3 p-4 bg-red-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">Subject:</span> {data.subject}</div>
          <div><span className="font-medium text-gray-700">From:</span> {data.from_name}</div>
          {data.warning && (
            <div className="text-red-600 font-medium">⚠️ {data.warning}</div>
          )}
        </div>
      );
    case 'calendar_event':
      return (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
          <div><span className="font-medium text-gray-700">Event:</span> {data.title}</div>
          <div><span className="font-medium text-gray-700">Date:</span> {data.date} at {data.start_time}</div>
          {data.duration_hours && <div><span className="font-medium text-gray-700">Duration:</span> {data.duration_hours}h</div>}
        </div>
      );
    default:
      return (
        <details className="mt-3">
          <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800">
            View details
          </summary>
          <pre className="mt-2 p-3 bg-gray-50 rounded-lg text-xs overflow-x-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      );
  }
}

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

  // Count pending for badge
  const pendingCount = approvals.filter(a => a.status === 'pending').length;

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
        <h1 className="text-2xl font-bold text-gray-900">
          Approvals
          {pendingCount > 0 && filter !== 'pending' && (
            <span className="ml-2 px-2 py-0.5 text-sm bg-amber-100 text-amber-700 rounded-full">
              {pendingCount} pending
            </span>
          )}
        </h1>
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
            {status === 'pending' && pendingCount > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs bg-amber-200 text-amber-800 rounded-full">
                {pendingCount}
              </span>
            )}
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
          {approvals.map((approval) => {
            const actionData = approval.action_data || approval.action_details;
            return (
              <div
                key={approval.id}
                className="bg-white rounded-xl border border-gray-200 p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Header: workflow name + status */}
                    <div className="flex items-center gap-2 mb-1">
                      {approval.workflow_name && (
                        <span className="text-xs text-gray-400 font-medium uppercase tracking-wide">
                          {approval.workflow_name}
                        </span>
                      )}
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

                    {/* Action type + summary */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-gray-400">
                        <ActionIcon type={actionData?.type} />
                      </span>
                      <span className="font-semibold text-gray-900">
                        {approval.node_type || 'Action'}
                      </span>
                      {approval.step_label && approval.step_label !== approval.node_type && (
                        <span className="text-gray-500 text-sm">— {approval.step_label}</span>
                      )}
                    </div>

                    {/* Summary message */}
                    <p className="text-gray-600 mb-2">
                      {approval.message || approval.action_summary || 'Action requires your approval'}
                    </p>

                    {/* Rich action preview */}
                    {actionData && <ActionPreview data={actionData} />}

                    <div className="text-sm text-gray-400 mt-3">
                      Requested {formatDate(approval.created_at)}
                    </div>

                    {/* Rejection reason */}
                    {approval.rejection_reason && (
                      <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-600">
                        Rejection reason: {approval.rejection_reason}
                      </div>
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
            );
          })}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <Info className="w-4 h-4" />
          About Approvals
        </h3>
        <p className="text-sm text-blue-700">
          Workflows pause at steps that require approval — like sending emails, creating payments, or making calls.
          You'll see exactly what's about to happen so you can review before it goes out.
          Toggle approval requirements per-step in the workflow editor.
        </p>
      </div>
    </div>
  );
}

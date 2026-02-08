import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date) {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDuration(ms: number) {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

export function getNodeIcon(type: string) {
  const icons: Record<string, string> = {
    start_manual: '▶️',
    start_form: '📝',
    send_email: '✉️',
    append_row: '📊',
    delay: '⏱️',
    send_notification: '🔔',
  };
  return icons[type] || '⚡';
}

export function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    paused: 'bg-amber-100 text-amber-800',
    waiting_approval: 'bg-purple-100 text-purple-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}

export function getFriendlyNodeType(type: string) {
  const names: Record<string, string> = {
    start_manual: 'Start',
    start_form: 'Form Submission',
    send_email: 'Send Email',
    append_row: 'Add to Spreadsheet',
    delay: 'Wait',
    send_notification: 'Send Notification',
  };
  return names[type] || type;
}

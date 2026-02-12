'use client';

import { useState, useEffect } from 'react';
import type { Node } from '@xyflow/react';

interface NodeInspectorProps {
  node: Node;
  onUpdate: (nodeId: string, data: any) => void;
  onDelete: (nodeId: string) => void;
  onClose: () => void;
  isAdvancedMode: boolean;
}

// Field configurations for different node types
const nodeConfigs: Record<string, { fields: { key: string; label: string; type: string; placeholder?: string; options?: string[] }[] }> = {
  start_email: {
    fields: [
      { key: 'from', label: 'From Email', type: 'text', placeholder: 'sender@example.com' },
      { key: 'subject', label: 'Subject Contains (optional)', type: 'text', placeholder: 'Leave empty for all emails' },
    ],
  },
  start_schedule: {
    fields: [
      { key: 'time', label: 'Time', type: 'text', placeholder: '09:00' },
      { key: 'frequency', label: 'Frequency', type: 'select', options: ['daily', 'weekly', 'monthly'] },
    ],
  },
  start_form: {
    fields: [
      { key: 'form_name', label: 'Form Name', type: 'text', placeholder: 'Contact Form' },
    ],
  },
  send_email: {
    fields: [
      { key: 'to', label: 'To', type: 'text', placeholder: '{{from}} or email@example.com' },
      { key: 'subject', label: 'Subject', type: 'text', placeholder: 'Re: {{subject}}' },
      { key: 'body', label: 'Message', type: 'textarea', placeholder: 'Write your email or use {{ai_response}}...' },
    ],
  },
  ai_reply: {
    fields: [
      { key: 'tone', label: 'Tone', type: 'select', options: ['professional', 'friendly', 'casual', 'formal'] },
      { key: 'context', label: 'Instructions', type: 'textarea', placeholder: 'Reply helpfully and offer to schedule a call...' },
    ],
  },
  ai_summarize: {
    fields: [
      { key: 'source', label: 'What to summarize', type: 'text', placeholder: 'the email content' },
      { key: 'format', label: 'Format', type: 'select', options: ['paragraph', 'bullet_points'] },
    ],
  },
  append_row: {
    fields: [
      { key: 'spreadsheet', label: 'Spreadsheet Name', type: 'text', placeholder: 'My Sales Log' },
      { key: 'sheet_name', label: 'Sheet Name', type: 'text', placeholder: 'Sheet1' },
    ],
  },
  read_sheet: {
    fields: [
      { key: 'spreadsheet_id', label: 'Spreadsheet ID', type: 'text', placeholder: '1BxiMVs0XRA5nFMd... (from URL)' },
      { key: 'range', label: 'Range', type: 'text', placeholder: 'Sheet1!A1:D10' },
    ],
  },
  send_slack: {
    fields: [
      { key: 'channel', label: 'Channel', type: 'text', placeholder: '#general' },
      { key: 'message', label: 'Message', type: 'textarea', placeholder: 'New email from {{from}}...' },
    ],
  },
  send_notification: {
    fields: [
      { key: 'message', label: 'Notification Message', type: 'textarea', placeholder: 'You have a new message...' },
    ],
  },
  delay: {
    fields: [
      { key: 'duration', label: 'Wait for', type: 'number', placeholder: '1' },
      { key: 'unit', label: 'Unit', type: 'select', options: ['minutes', 'hours', 'days'] },
    ],
  },
  condition: {
    fields: [
      { key: 'condition', label: 'Condition', type: 'text', placeholder: 'if {{status}} == "approved"' },
    ],
  },
  approval: {
    fields: [
      { key: 'message', label: 'Approval Message', type: 'textarea', placeholder: 'Describe what needs approval...' },
      { key: 'timeout', label: 'Timeout (hours)', type: 'number', placeholder: '24' },
    ],
  },
  http_request: {
    fields: [
      { key: 'url', label: 'URL', type: 'text', placeholder: 'https://api.example.com/endpoint' },
      { key: 'method', label: 'Method', type: 'select', options: ['GET', 'POST', 'PUT', 'DELETE'] },
    ],
  },
};

export default function NodeInspector({
  node,
  onUpdate,
  onDelete,
  onClose,
  isAdvancedMode,
}: NodeInspectorProps) {
  const [config, setConfig] = useState<Record<string, any>>(node.data.config || {});
  const [label, setLabel] = useState<string>(typeof node.data.label === 'string' ? node.data.label : '');

  // Re-sync when node changes
  useEffect(() => {
    setConfig(node.data.config || {});
    setLabel(typeof node.data.label === 'string' ? node.data.label : '');
  }, [node.id, node.data.config, node.data.label]);

  const nodeType = node.data.nodeType as string;
  const fieldConfig = nodeConfigs[nodeType] || { fields: [] };

  const handleFieldChange = (key: string, value: any) => {
    // Only keep fields that are valid for this node type
    const validFields = fieldConfig.fields.map((f: any) => f.key);
    const cleanConfig: Record<string, any> = {};
    
    // Copy only valid fields from existing config
    for (const fieldKey of validFields) {
      if (config[fieldKey] !== undefined) {
        cleanConfig[fieldKey] = config[fieldKey];
      }
    }
    
    // Update the changed field
    cleanConfig[key] = value;
    
    setConfig(cleanConfig);
    onUpdate(node.id, { config: cleanConfig });
  };

  const handleLabelChange = (newLabel: string) => {
    setLabel(newLabel);
    onUpdate(node.id, { label: newLabel });
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      <div className="border-b border-gray-100 px-4 py-3 flex items-center justify-between">
        <h3 className="font-semibold">Step Settings</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {/* Label */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Step Name
          </label>
          <input
            type="text"
            value={label}
            onChange={(e) => handleLabelChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Type indicator */}
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-500 uppercase tracking-wider">Type</div>
          <div className="font-medium">{nodeType}</div>
        </div>

        {/* Fields */}
        {fieldConfig.fields.map((field) => (
          <div key={field.key} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            {field.type === 'select' ? (
              <select
                value={config[field.key] || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select...</option>
                {field.options?.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : field.type === 'textarea' ? (
              <textarea
                value={config[field.key] || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                rows={3}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            ) : (
              <input
                type={field.type}
                value={config[field.key] || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            )}
          </div>
        ))}

        {/* Advanced: Raw JSON */}
        {isAdvancedMode && (
          <div className="mt-6 pt-4 border-t border-gray-100">
            <details>
              <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                Raw Configuration (JSON)
              </summary>
              <textarea
                value={JSON.stringify(config, null, 2)}
                onChange={(e) => {
                  try {
                    const parsed = JSON.parse(e.target.value);
                    setConfig(parsed);
                    onUpdate(node.id, { config: parsed });
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                rows={6}
                className="mt-2 w-full px-3 py-2 border border-gray-200 rounded-lg font-mono text-xs focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </details>
          </div>
        )}
      </div>

      {/* Delete Button */}
      <div className="border-t border-gray-100 p-4">
        <button
          onClick={() => onDelete(node.id)}
          className="w-full px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100"
        >
          Delete Step
        </button>
      </div>
    </div>
  );
}

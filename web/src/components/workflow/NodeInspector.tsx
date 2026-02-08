'use client';

import { useState } from 'react';
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
  send_email: {
    fields: [
      { key: 'to', label: 'To', type: 'text', placeholder: 'email@example.com' },
      { key: 'subject', label: 'Subject', type: 'text', placeholder: 'Email subject' },
      { key: 'body', label: 'Message', type: 'textarea', placeholder: 'Write your email...' },
    ],
  },
  send_sms: {
    fields: [
      { key: 'phone', label: 'Phone Number', type: 'text', placeholder: '+1234567890' },
      { key: 'message', label: 'Message', type: 'textarea', placeholder: 'SMS message...' },
    ],
  },
  update_spreadsheet: {
    fields: [
      { key: 'spreadsheet', label: 'Spreadsheet', type: 'select', options: ['My Sales Log', 'Customer List', 'Inventory'] },
      { key: 'action', label: 'Action', type: 'select', options: ['Add Row', 'Update Row', 'Delete Row'] },
    ],
  },
  wait: {
    fields: [
      { key: 'duration', label: 'Wait for', type: 'number', placeholder: '1' },
      { key: 'unit', label: 'Unit', type: 'select', options: ['minutes', 'hours', 'days'] },
    ],
  },
  schedule: {
    fields: [
      { key: 'cron', label: 'Schedule', type: 'select', options: ['Every day at 9am', 'Every Monday', 'Every hour', 'Custom'] },
    ],
  },
  if_else: {
    fields: [
      { key: 'field', label: 'Check if', type: 'text', placeholder: 'Field name' },
      { key: 'operator', label: 'Is', type: 'select', options: ['equals', 'not equals', 'contains', 'greater than', 'less than'] },
      { key: 'value', label: 'Value', type: 'text', placeholder: 'Value to compare' },
    ],
  },
  approval: {
    fields: [
      { key: 'message', label: 'Approval Message', type: 'textarea', placeholder: 'Describe what needs approval...' },
      { key: 'timeout', label: 'Timeout (hours)', type: 'number', placeholder: '24' },
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
  const [config, setConfig] = useState(node.data.config || {});
  const [label, setLabel] = useState(node.data.label || '');

  const nodeType = node.data.nodeType;
  const fieldConfig = nodeConfigs[nodeType] || { fields: [] };

  const handleFieldChange = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    onUpdate(node.id, { config: newConfig });
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

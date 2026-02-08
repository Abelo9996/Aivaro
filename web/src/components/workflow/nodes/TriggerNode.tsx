'use client';

import { Handle, Position } from '@xyflow/react';

interface TriggerNodeProps {
  data: {
    label: string;
    nodeType: string;
    config: Record<string, any>;
  };
  selected?: boolean;
}

const triggerIcons: Record<string, string> = {
  form_submit: '📝',
  schedule: '⏰',
  email_received: '📧',
  manual_trigger: '👆',
  webhook: '🔗',
};

export default function TriggerNode({ data, selected }: TriggerNodeProps) {
  const icon = triggerIcons[data.nodeType] || '⚡';

  return (
    <div
      className={`bg-gradient-to-br from-green-50 to-emerald-50 border-2 rounded-xl px-4 py-3 min-w-[180px] shadow-sm ${
        selected ? 'border-green-500 ring-2 ring-green-200' : 'border-green-200'
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-xl">{icon}</span>
        <div>
          <div className="text-xs text-green-600 font-medium uppercase tracking-wider">
            Start
          </div>
          <div className="font-medium text-gray-900">{data.label}</div>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-green-500 border-2 border-white"
      />
    </div>
  );
}

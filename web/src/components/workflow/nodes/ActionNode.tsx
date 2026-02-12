'use client';

import { Handle, Position } from '@xyflow/react';
import ServiceIcon from '@/components/ui/ServiceIcon';

interface ActionNodeProps {
  data: {
    label: string;
    nodeType: string;
    config: Record<string, any>;
  };
  selected?: boolean;
}

export default function ActionNode({ data, selected }: ActionNodeProps) {
  return (
    <div
      className={`bg-white border-2 rounded-xl px-4 py-3 min-w-[180px] shadow-sm ${
        selected ? 'border-primary-500 ring-2 ring-primary-200' : 'border-gray-200'
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-gray-400 border-2 border-white"
      />
      <div className="flex items-center gap-2">
        <ServiceIcon type={data.nodeType} size={24} />
        <div>
          <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">
            Action
          </div>
          <div className="font-medium text-gray-900">{data.label}</div>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-gray-400 border-2 border-white"
      />
    </div>
  );
}

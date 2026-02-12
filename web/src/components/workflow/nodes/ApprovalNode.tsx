'use client';

import { Handle, Position } from '@xyflow/react';
import ServiceIcon from '@/components/ui/ServiceIcon';

interface ApprovalNodeProps {
  data: {
    label: string;
    nodeType: string;
    config: Record<string, any>;
  };
  selected?: boolean;
}

export default function ApprovalNode({ data, selected }: ApprovalNodeProps) {
  return (
    <div
      className={`bg-gradient-to-br from-amber-50 to-orange-50 border-2 rounded-xl px-4 py-3 min-w-[180px] shadow-sm ${
        selected ? 'border-amber-500 ring-2 ring-amber-200' : 'border-amber-200'
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-amber-400 border-2 border-white"
      />
      <div className="flex items-center gap-2">
        <ServiceIcon type="approval" size={24} />
        <div>
          <div className="text-xs text-amber-600 font-medium uppercase tracking-wider">
            Approval
          </div>
          <div className="font-medium text-gray-900">{data.label}</div>
        </div>
      </div>
      <div className="mt-2 text-xs text-amber-600">
        Pauses until you approve
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-amber-500 border-2 border-white"
      />
    </div>
  );
}

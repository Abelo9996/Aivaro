'use client';

import { Handle, Position } from '@xyflow/react';
import ServiceIcon from '@/components/ui/ServiceIcon';

interface ConditionNodeProps {
  data: {
    label: string;
    nodeType: string;
    config: Record<string, any>;
  };
  selected?: boolean;
}

export default function ConditionNode({ data, selected }: ConditionNodeProps) {
  return (
    <div
      className={`bg-gradient-to-br from-purple-50 to-indigo-50 border-2 rounded-xl px-4 py-3 min-w-[180px] shadow-sm ${
        selected ? 'border-purple-500 ring-2 ring-purple-200' : 'border-purple-200'
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-purple-400 border-2 border-white"
      />
      <div className="flex items-center gap-2">
        <ServiceIcon type="condition" size={24} />
        <div>
          <div className="text-xs text-purple-600 font-medium uppercase tracking-wider">
            Condition
          </div>
          <div className="font-medium text-gray-900">{data.label}</div>
        </div>
      </div>
      <div className="flex justify-between mt-3 text-xs">
        <div className="flex flex-col items-center">
          <span className="text-green-600 font-medium">Yes</span>
          <Handle
            type="source"
            position={Position.Bottom}
            id="yes"
            className="w-3 h-3 !bg-green-500 border-2 border-white !relative !transform-none !left-0 !-bottom-1"
          />
        </div>
        <div className="flex flex-col items-center">
          <span className="text-red-600 font-medium">No</span>
          <Handle
            type="source"
            position={Position.Bottom}
            id="no"
            className="w-3 h-3 !bg-red-500 border-2 border-white !relative !transform-none !right-0 !-bottom-1"
          />
        </div>
      </div>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { CheckCircle, Circle, Loader2, XCircle, Play } from 'lucide-react';

interface Step {
  node_id: string;
  node_label: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

interface ExecutionProgressProps {
  isOpen: boolean;
  workflowName: string;
  totalSteps: number;
  completedSteps: number;
  currentStep?: string;
  steps: Step[];
  status: 'running' | 'completed' | 'failed';
  onClose: () => void;
  onViewExecution?: () => void;
  executionId?: string;
}

export default function ExecutionProgress({
  isOpen,
  workflowName,
  totalSteps,
  completedSteps,
  currentStep,
  steps,
  status,
  onClose,
  onViewExecution,
  executionId,
}: ExecutionProgressProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const targetProgress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;
    // Animate progress
    const timer = setTimeout(() => {
      setProgress(targetProgress);
    }, 100);
    return () => clearTimeout(timer);
  }, [completedSteps, totalSteps]);

  if (!isOpen) return null;

  const getStepIcon = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-indigo-500 animate-spin" />;
      default:
        return <Circle className="h-5 w-5 text-gray-300" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
          <div className="flex items-center gap-3">
            {status === 'running' ? (
              <Loader2 className="h-6 w-6 text-white animate-spin" />
            ) : status === 'completed' ? (
              <CheckCircle className="h-6 w-6 text-white" />
            ) : (
              <XCircle className="h-6 w-6 text-white" />
            )}
            <div>
              <h3 className="text-white font-semibold">
                {status === 'running' ? 'Running Workflow' : status === 'completed' ? 'Workflow Complete!' : 'Workflow Failed'}
              </h3>
              <p className="text-indigo-100 text-sm">{workflowName}</p>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{completedSteps} of {totalSteps} steps</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ease-out rounded-full ${
                status === 'failed' ? 'bg-red-500' : 
                status === 'completed' ? 'bg-green-500' : 
                'bg-gradient-to-r from-indigo-500 to-purple-500'
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>
          {currentStep && status === 'running' && (
            <p className="text-sm text-gray-500 mt-2 flex items-center gap-2">
              <Play className="h-3 w-3" />
              Running: {currentStep}
            </p>
          )}
        </div>

        {/* Steps List */}
        <div className="px-6 pb-4 max-h-60 overflow-y-auto">
          <div className="space-y-2">
            {steps.map((step, index) => (
              <div 
                key={step.node_id} 
                className={`flex items-center gap-3 p-2 rounded-lg transition-colors ${
                  step.status === 'running' ? 'bg-indigo-50' : 
                  step.status === 'completed' ? 'bg-green-50' :
                  step.status === 'failed' ? 'bg-red-50' : 'bg-gray-50'
                }`}
              >
                <span className="text-gray-400 text-sm w-6">{index + 1}.</span>
                {getStepIcon(step.status)}
                <span className={`flex-1 text-sm ${
                  step.status === 'pending' ? 'text-gray-400' : 'text-gray-700'
                }`}>
                  {step.node_label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          {status !== 'running' && (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm font-medium"
              >
                Close
              </button>
              {executionId && onViewExecution && (
                <button
                  onClick={onViewExecution}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
                >
                  View Details
                </button>
              )}
            </>
          )}
          {status === 'running' && (
            <p className="text-sm text-gray-500 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Please wait...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

interface GeneratedWorkflow {
  workflowName: string;
  summary: string;
  nodes: any[];
  edges: any[];
}

interface AIWorkflowGeneratorProps {
  onGenerate: (workflow: GeneratedWorkflow) => void;
  onCancel: () => void;
}

const EXAMPLE_PROMPTS = [
  "Send a welcome email when someone fills out my contact form, then follow up after 3 days if they haven't responded",
  "When I get a new order, log it to my spreadsheet and send a confirmation email to the customer",
  "Send me a daily summary of new leads from my website form",
  "When a booking is made, confirm with the customer and notify my team on Slack",
  "Follow up with customers who haven't purchased in 30 days",
];

export default function AIWorkflowGenerator({ onGenerate, onCancel }: AIWorkflowGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedWorkflow, setGeneratedWorkflow] = useState<GeneratedWorkflow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'input' | 'preview'>('input');

  const handleGenerate = async () => {
    if (!prompt.trim() || prompt.length < 10) {
      setError('Please describe your workflow in more detail (at least 10 characters)');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const result = await api.generateWorkflow(prompt);
      setGeneratedWorkflow(result);
      setStep('preview');
    } catch (err: any) {
      setError(err.message || 'Failed to generate workflow. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUseWorkflow = () => {
    if (generatedWorkflow) {
      onGenerate(generatedWorkflow);
    }
  };

  const handleRegenerate = () => {
    setGeneratedWorkflow(null);
    setStep('input');
  };

  const getNodeIcon = (type: string) => {
    const icons: Record<string, string> = {
      start_manual: '▶️',
      start_form: '📝',
      start_schedule: '⏰',
      send_email: '📧',
      append_row: '📊',
      delay: '⏳',
      send_notification: '🔔',
      send_slack: '💬',
      http_request: '🌐',
      condition: '🔀',
      ai_summarize: '🤖',
    };
    return icons[type] || '⚡';
  };

  if (step === 'preview' && generatedWorkflow) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-500 to-purple-600 text-white p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <span className="text-2xl">✨</span>
              </div>
              <div>
                <h2 className="text-xl font-bold">{generatedWorkflow.workflowName}</h2>
                <p className="text-white/80 text-sm">{generatedWorkflow.summary}</p>
              </div>
            </div>
          </div>

          {/* Workflow Preview */}
          <div className="p-6 max-h-[400px] overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4">Workflow Steps</h3>
            <div className="space-y-3">
              {generatedWorkflow.nodes.map((node, index) => (
                <div 
                  key={node.id} 
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-lg">
                    {getNodeIcon(node.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 truncate">{node.label}</div>
                    <div className="text-xs text-gray-500 capitalize">{node.type.replace('_', ' ')}</div>
                  </div>
                  <div className="text-xs text-gray-400">
                    Step {index + 1}
                  </div>
                </div>
              ))}
            </div>

            {/* Connection visualization */}
            <div className="mt-4 p-3 bg-primary-50 rounded-lg">
              <div className="text-xs text-primary-700">
                <strong>{generatedWorkflow.nodes.length} steps</strong> connected with{' '}
                <strong>{generatedWorkflow.edges.length} connections</strong>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3">
            <button
              onClick={handleRegenerate}
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors font-medium"
            >
              🔄 Regenerate
            </button>
            <button
              onClick={onCancel}
              className="px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleUseWorkflow}
              className="flex-1 px-4 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium"
            >
              ✨ Use This Workflow
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-purple-600 text-white p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <span className="text-2xl">🪄</span>
            </div>
            <div>
              <h2 className="text-xl font-bold">Generate Workflow with AI</h2>
              <p className="text-white/80 text-sm">Describe what you want to automate in plain English</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to automate?
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., When someone fills out my contact form, send them a welcome email and add their info to my spreadsheet..."
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-gray-900"
              rows={4}
              disabled={isGenerating}
            />
            {error && (
              <p className="mt-2 text-sm text-red-500">{error}</p>
            )}
          </div>

          {/* Example prompts */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Try one of these examples:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.slice(0, 3).map((example, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(example)}
                  disabled={isGenerating}
                  className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors truncate max-w-[200px]"
                  title={example}
                >
                  {example.slice(0, 40)}...
                </button>
              ))}
            </div>
          </div>

          {/* AI indicator */}
          {isGenerating && (
            <div className="mb-4 p-4 bg-primary-50 rounded-xl">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center animate-pulse">
                  <span className="text-white text-sm">🤖</span>
                </div>
                <div>
                  <div className="font-medium text-primary-900">Generating your workflow...</div>
                  <div className="text-sm text-primary-600">AI is creating the perfect automation for you</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3">
          <button
            onClick={onCancel}
            disabled={isGenerating}
            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors font-medium disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim()}
            className="flex-1 px-4 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                ✨ Generate Workflow
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

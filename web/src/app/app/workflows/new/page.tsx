'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Wand2, Plus, LayoutTemplate, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import AIWorkflowGenerator from '@/components/workflow/AIWorkflowGenerator';

type CreationMethod = 'ai' | 'scratch' | 'template' | null;

export default function NewWorkflowPage() {
  const router = useRouter();
  const [method, setMethod] = useState<CreationMethod>(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleAIGenerate = async (workflow: any) => {
    setIsCreating(true);
    try {
      // Create the workflow with the generated data
      const created = await api.createWorkflow({
        name: workflow.workflowName,
        description: workflow.summary,
        nodes: workflow.nodes,
        edges: workflow.edges,
      });
      
      // Navigate to the workflow editor
      router.push(`/app/workflows/${created.id}`);
    } catch (err) {
      console.error('Failed to create workflow:', err);
      setIsCreating(false);
    }
  };

  const handleCreateBlank = async () => {
    setIsCreating(true);
    try {
      // Create a blank workflow with just a start node
      const created = await api.createWorkflow({
        name: 'Untitled Workflow',
        description: '',
        nodes: [
          {
            id: 'start-1',
            type: 'start_manual',
            label: 'When you run this workflow',
            position: { x: 250, y: 50 },
            parameters: {},
            requiresApproval: false,
          }
        ],
        edges: [],
      });
      
      router.push(`/app/workflows/${created.id}`);
    } catch (err) {
      console.error('Failed to create workflow:', err);
      setIsCreating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <Link
          href="/app/workflows"
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          ← Back to Workflows
        </Link>
      </div>

      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Create a New Workflow</h1>
        <p className="text-gray-500 text-lg">Choose how you'd like to get started</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* AI Generate */}
        <button
          onClick={() => setMethod('ai')}
          disabled={isCreating}
          className="group relative bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl p-6 text-left text-white hover:shadow-lg hover:scale-[1.02] transition-all disabled:opacity-50"
        >
          <div className="absolute top-3 right-3 bg-white/20 text-xs px-2 py-1 rounded-full flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> Recommended
          </div>
          <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Wand2 className="w-7 h-7" />
          </div>
          <h3 className="text-xl font-bold mb-2">Generate with AI</h3>
          <p className="text-white/80 text-sm">
            Describe what you want to automate in plain English and let AI create the workflow for you.
          </p>
          <div className="mt-4 text-xs text-white/60">
            Best for: Quick setup, complex automations
          </div>
        </button>

        {/* From Scratch */}
        <button
          onClick={handleCreateBlank}
          disabled={isCreating}
          className="group bg-white border-2 border-gray-200 rounded-2xl p-6 text-left hover:border-primary-300 hover:shadow-lg hover:scale-[1.02] transition-all disabled:opacity-50"
        >
          <div className="w-14 h-14 bg-gray-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary-50 transition-colors">
            <span className="text-3xl">🔧</span>
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Start from Scratch</h3>
          <p className="text-gray-500 text-sm">
            Build your workflow step by step using our visual drag-and-drop editor.
          </p>
          <div className="mt-4 text-xs text-gray-400">
            Best for: Custom workflows, full control
          </div>
        </button>

        {/* From Template */}
        <Link
          href="/app/templates"
          className="group bg-white border-2 border-gray-200 rounded-2xl p-6 text-left hover:border-primary-300 hover:shadow-lg hover:scale-[1.02] transition-all"
        >
          <div className="w-14 h-14 bg-gray-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary-50 transition-colors">
            <span className="text-3xl">📋</span>
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Use a Template</h3>
          <p className="text-gray-500 text-sm">
            Start with a pre-built workflow designed for common business tasks.
          </p>
          <div className="mt-4 text-xs text-gray-400">
            Best for: Common use cases, fast start
          </div>
        </Link>
      </div>

      {/* Quick Examples */}
      <div className="mt-12 text-center">
        <p className="text-sm text-gray-400 mb-4">Popular automations created with AI:</p>
        <div className="flex flex-wrap justify-center gap-2">
          {[
            'Lead follow-up sequence',
            'Customer onboarding',
            'Order notifications',
            'Meeting reminders',
            'Weekly reports',
          ].map((example) => (
            <button
              key={example}
              onClick={() => setMethod('ai')}
              className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* AI Generator Modal */}
      {method === 'ai' && (
        <AIWorkflowGenerator
          onGenerate={handleAIGenerate}
          onCancel={() => setMethod(null)}
        />
      )}

      {/* Creating Indicator */}
      {isCreating && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="bg-white rounded-xl p-8 text-center shadow-xl">
            <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Creating your workflow...</p>
          </div>
        </div>
      )}
    </div>
  );
}

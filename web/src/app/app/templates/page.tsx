'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Zap } from 'lucide-react';
import { api } from '@/lib/api';
import type { Template } from '@/types';

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [creatingId, setCreatingId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setError(null);
      const data = await api.templates.list();
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates:', err);
      setError('Failed to load templates. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...Array.from(new Set(templates.map(t => t.category).filter(Boolean)))];
  
  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(t => t.category === selectedCategory);

  const handleUseTemplate = async (template: Template) => {
    try {
      setCreatingId(template.id);
      const workflow = await api.createWorkflowFromTemplate(template.id);
      router.push(`/app/workflows/${workflow.id}`);
    } catch (err) {
      console.error('Failed to create workflow from template:', err);
      setError('Failed to create workflow. Please try again.');
      setCreatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-gray-500">
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Loading templates...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <p className="text-red-500 mb-4">{error}</p>
        <button 
          onClick={loadTemplates}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="overflow-x-hidden">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Templates</h1>
        <p className="text-gray-500">
          Start with a pre-built automation and customize it for your business.
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition flex-shrink-0 ${
              selectedCategory === cat
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
            }`}
          >
            {cat === 'all' ? 'All Templates' : cat}
          </button>
        ))}
      </div>

      {/* Templates Grid */}
      <div 
        data-walkthrough="templates-grid"
        className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {filteredTemplates.map((template, index) => (
          <div
            key={template.id}
            data-walkthrough={index === 0 ? "template-card" : undefined}
            className="bg-white rounded-xl border border-gray-200 p-6 hover:border-primary-300 hover:shadow-md transition group overflow-hidden"
          >
            <div className="w-12 h-12 bg-gradient-to-br from-primary-100 to-purple-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <Zap className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="font-semibold mb-2 text-gray-900 truncate">{template.name}</h3>
            <p className="text-sm text-gray-500 mb-4 line-clamp-2">
              {template.description}
            </p>
            <div className="flex items-center gap-2 mb-4 flex-wrap">
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full truncate max-w-[120px]">
                {template.category}
              </span>
              <span className="text-xs text-gray-400">
                {template.definition?.nodes?.length || 0} steps
              </span>
            </div>
            <button
              onClick={() => handleUseTemplate(template)}
              disabled={creatingId === template.id}
              className="w-full bg-primary-600 text-white py-2 rounded-lg font-medium hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {creatingId === template.id ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </>
              ) : (
                'Use Template'
              )}
            </button>
          </div>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No templates found in this category.</p>
        </div>
      )}

      {/* Custom Workflow Option */}
      <div className="mt-12 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-8 text-center">
        <h3 className="text-lg font-semibold mb-2">Need something custom?</h3>
        <p className="text-gray-500 mb-4">
          Build your own workflow from scratch with our visual editor.
        </p>
        <Link
          href="/app/workflows/new"
          className="inline-block bg-gray-900 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-800 transition"
        >
          Create Custom Workflow
        </Link>
      </div>
    </div>
  );
}

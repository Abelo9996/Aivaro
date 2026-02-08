'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { Template } from '@/types';

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await api.templates.list();
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...Array.from(new Set(templates.map(t => t.category)))];
  
  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(t => t.category === selectedCategory);

  const handleUseTemplate = async (template: Template) => {
    try {
      const workflow = await api.createWorkflowFromTemplate(template.id);
      window.location.href = `/app/workflows/${workflow.id}`;
    } catch (err) {
      console.error('Failed to create workflow from template:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading templates...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Templates</h1>
        <p className="text-gray-500">
          Start with a pre-built automation and customize it for your business.
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
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
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <div
            key={template.id}
            className="bg-white rounded-xl border border-gray-200 p-6 hover:border-primary-300 hover:shadow-sm transition"
          >
            <div className="text-3xl mb-4">{template.icon || '⚡'}</div>
            <h3 className="font-semibold mb-2">{template.name}</h3>
            <p className="text-sm text-gray-500 mb-4 line-clamp-2">
              {template.description}
            </p>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                {template.category}
              </span>
              <span className="text-xs text-gray-400">
                {template.definition.nodes?.length || 0} steps
              </span>
            </div>
            <button
              onClick={() => handleUseTemplate(template)}
              className="w-full bg-primary-600 text-white py-2 rounded-lg font-medium hover:bg-primary-700 transition"
            >
              Use Template
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
      <div className="mt-12 bg-gray-50 rounded-xl p-8 text-center">
        <h3 className="text-lg font-semibold mb-2">Need something custom?</h3>
        <p className="text-gray-500 mb-4">
          Build your own workflow from scratch with our visual editor.
        </p>
        <Link
          href="/app/workflows/new"
          className="inline-block bg-gray-900 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-800"
        >
          Create Custom Workflow
        </Link>
      </div>
    </div>
  );
}

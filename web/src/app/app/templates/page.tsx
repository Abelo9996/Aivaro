'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Target, 
  TrendingUp, 
  Users, 
  Mail, 
  ShoppingCart, 
  Calendar, 
  FileText, 
  MessageSquare, 
  Bell, 
  CreditCard,
  Briefcase,
  Clock,
  Star,
  Gift,
  Megaphone,
  BarChart3,
  Zap,
  type LucideIcon
} from 'lucide-react';
import { api } from '@/lib/api';
import type { Template } from '@/types';

// Map categories and template names to appropriate icons
const getTemplateIcon = (template: Template): LucideIcon => {
  const category = template.category?.toLowerCase() || '';
  const name = template.name?.toLowerCase() || '';
  
  // Check by category first
  if (category.includes('lead') || category.includes('sales')) {
    if (name.includes('pipeline') || name.includes('tracker')) return TrendingUp;
    if (name.includes('referral')) return Users;
    return Target;
  }
  if (category.includes('customer') || category.includes('retention')) {
    if (name.includes('feedback') || name.includes('review')) return Star;
    if (name.includes('birthday') || name.includes('loyalty')) return Gift;
    return Users;
  }
  if (category.includes('email') || category.includes('newsletter')) return Mail;
  if (category.includes('ecommerce') || category.includes('order')) return ShoppingCart;
  if (category.includes('booking') || category.includes('appointment') || category.includes('scheduling')) return Calendar;
  if (category.includes('invoice') || category.includes('payment')) return CreditCard;
  if (category.includes('onboarding')) return Briefcase;
  if (category.includes('notification') || category.includes('alert')) return Bell;
  if (category.includes('support') || category.includes('chat')) return MessageSquare;
  if (category.includes('content') || category.includes('social')) return Megaphone;
  if (category.includes('report') || category.includes('analytics')) return BarChart3;
  if (category.includes('reminder') || category.includes('follow')) return Clock;
  if (category.includes('document') || category.includes('contract')) return FileText;
  
  // Check by name keywords
  if (name.includes('lead') || name.includes('capture')) return Target;
  if (name.includes('sales') || name.includes('pipeline')) return TrendingUp;
  if (name.includes('email') || name.includes('newsletter')) return Mail;
  if (name.includes('order') || name.includes('cart') || name.includes('purchase')) return ShoppingCart;
  if (name.includes('booking') || name.includes('appointment') || name.includes('calendar')) return Calendar;
  if (name.includes('invoice') || name.includes('payment')) return CreditCard;
  if (name.includes('onboard') || name.includes('welcome')) return Briefcase;
  if (name.includes('notify') || name.includes('alert')) return Bell;
  if (name.includes('support') || name.includes('ticket')) return MessageSquare;
  if (name.includes('review') || name.includes('feedback')) return Star;
  if (name.includes('referral')) return Users;
  if (name.includes('reminder') || name.includes('follow')) return Clock;
  
  // Default
  return Zap;
};

// Get icon background color based on category
const getIconColors = (category: string): string => {
  const cat = category?.toLowerCase() || '';
  if (cat.includes('lead') || cat.includes('sales')) return 'from-orange-100 to-red-100 text-orange-600';
  if (cat.includes('customer') || cat.includes('retention')) return 'from-pink-100 to-rose-100 text-pink-600';
  if (cat.includes('email') || cat.includes('newsletter')) return 'from-blue-100 to-indigo-100 text-blue-600';
  if (cat.includes('ecommerce') || cat.includes('order')) return 'from-green-100 to-emerald-100 text-green-600';
  if (cat.includes('booking') || cat.includes('scheduling')) return 'from-purple-100 to-violet-100 text-purple-600';
  if (cat.includes('onboarding')) return 'from-cyan-100 to-teal-100 text-cyan-600';
  if (cat.includes('support')) return 'from-amber-100 to-yellow-100 text-amber-600';
  return 'from-primary-100 to-purple-100 text-primary-600';
};

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
    } catch (err: any) {
      console.error('Failed to create workflow from template:', err);
      const message = err?.detail?.message || err?.message || 'Failed to create workflow. Please try again.';
      setError(message);
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
    <div className="max-w-full overflow-x-hidden">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Templates</h1>
        <p className="text-gray-500 text-sm">
          Start with a pre-built automation and customize it for your business.
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-hide -mx-1 px-1">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition flex-shrink-0 ${
              selectedCategory === cat
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
            }`}
          >
            {cat === 'all' ? 'All Templates' : cat}
          </button>
        ))}
      </div>

      {/* Templates Grid - More compact */}
      <div 
        data-walkthrough="templates-grid"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
      >
        {filteredTemplates.map((template, index) => {
          const IconComponent = getTemplateIcon(template);
          const iconColors = getIconColors(template.category || '');
          
          return (
            <div
              key={template.id}
              data-walkthrough={index === 0 ? "template-card" : undefined}
              className="bg-white rounded-xl border border-gray-200 p-4 hover:border-primary-300 hover:shadow-md transition group"
            >
              <div className="flex items-start gap-3 mb-3">
                <div className={`w-10 h-10 bg-gradient-to-br ${iconColors} rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition`}>
                  <IconComponent className="w-5 h-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-sm text-gray-900 truncate">{template.name}</h3>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-gray-500 truncate">
                      {template.category}
                    </span>
                    <span className="text-xs text-gray-400">
                      · {template.definition?.nodes?.length || 0} steps
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 mb-3 line-clamp-2 min-h-[2.5rem]">
                {template.description}
              </p>
              <button
                onClick={() => handleUseTemplate(template)}
                disabled={creatingId === template.id}
                className="w-full bg-primary-600 text-white py-1.5 rounded-lg text-sm font-medium hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {creatingId === template.id ? (
                  <>
                    <svg className="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
          );
        })}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No templates found in this category.</p>
        </div>
      )}

      {/* Custom Workflow Option */}
      <div className="mt-8 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 text-center">
        <h3 className="text-base font-semibold mb-1">Need something custom?</h3>
        <p className="text-gray-500 text-sm mb-3">
          Build your own workflow from scratch with our visual editor.
        </p>
        <Link
          href="/app/workflows/new"
          className="inline-block bg-gray-900 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition"
        >
          Create Custom Workflow
        </Link>
      </div>
    </div>
  );
}

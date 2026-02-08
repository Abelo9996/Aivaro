'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import type { Template } from '@/types';

const BUSINESS_TYPES = [
  { id: 'service', label: 'Service Business', description: 'Consultants, coaches, agencies' },
  { id: 'resale', label: 'Resale / E-commerce', description: 'Selling products online or offline' },
  { id: 'agency', label: 'Agency / Studio', description: 'Creative or marketing agency' },
  { id: 'saas', label: 'SaaS / Software', description: 'Software product business' },
  { id: 'other', label: 'Other', description: 'Something else' },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { user, updateUser, checkAuth } = useAuthStore();
  const [step, setStep] = useState(1);
  const [businessType, setBusinessType] = useState('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (businessType) {
      loadTemplates();
    }
  }, [businessType]);

  const loadTemplates = async () => {
    try {
      const data = await api.getTemplates(undefined, businessType);
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const handleBusinessSelect = async (type: string) => {
    setBusinessType(type);
    await updateUser({ business_type: type });
    setStep(2);
  };

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    setStep(3);
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      let workflowId = null;
      if (selectedTemplate) {
        const workflow = await api.useTemplate(selectedTemplate.id);
        workflowId = workflow.id;
      }
      await updateUser({ onboarding_completed: true });
      
      if (workflowId) {
        router.push(`/app/workflows/${workflowId}`);
      } else {
        router.push('/app');
      }
    } catch (err) {
      console.error('Failed to complete onboarding:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`w-3 h-3 rounded-full ${
                  s <= step ? 'bg-primary-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-center text-sm text-gray-500 mt-2">
            Step {step} of 3
          </p>
        </div>

        {/* Step 1: Business Type */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
            <h1 className="text-2xl font-bold text-center mb-2">
              What kind of business are you?
            </h1>
            <p className="text-gray-500 text-center mb-8">
              This helps us show you the most relevant automations.
            </p>

            <div className="space-y-3">
              {BUSINESS_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => handleBusinessSelect(type.id)}
                  className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
                >
                  <div className="font-medium">{type.label}</div>
                  <div className="text-sm text-gray-500">{type.description}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Pick Template */}
        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
            <h1 className="text-2xl font-bold text-center mb-2">
              Pick your first automation
            </h1>
            <p className="text-gray-500 text-center mb-8">
              Start with a template and customize it later.
            </p>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {templates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => handleTemplateSelect(template)}
                  className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
                >
                  <div className="font-medium">{template.title}</div>
                  <div className="text-sm text-gray-500 mt-1">{template.summary}</div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                      {template.category}
                    </span>
                  </div>
                </button>
              ))}
            </div>

            <button
              onClick={() => setStep(3)}
              className="w-full mt-6 py-3 text-gray-600 hover:text-gray-900"
            >
              Skip for now
            </button>
          </div>
        )}

        {/* Step 3: Ready */}
        {step === 3 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h1 className="text-2xl font-bold mb-2">You're all set!</h1>
            <p className="text-gray-500 mb-8">
              {selectedTemplate
                ? `We'll set up "${selectedTemplate.title}" for you. You can test it before turning it on.`
                : "Let's create your first automation."}
            </p>

            <button
              onClick={handleComplete}
              disabled={loading}
              className="bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Setting up...' : 'Get Started →'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

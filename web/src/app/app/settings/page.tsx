'use client';

import { useEffect, useState } from 'react';
import { User, Mail, Building2, CreditCard, Shield, ExternalLink } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';

interface UsageData {
  plan: string;
  is_trial: boolean;
  is_unlimited: boolean;
  trial_expired: boolean;
  trial_days_left: number;
  usage: {
    active_workflows: { used: number; limit: number };
    total_runs: { used: number; limit: number };
    knowledge_entries: { used: number; limit: number };
  };
  features: {
    agent_tasks: boolean;
    file_import: boolean;
  };
}

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [fullName, setFullName] = useState('');
  const [businessType, setBusinessType] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usageData] = await Promise.all([
        api.request<UsageData>('/api/auth/me/usage', { method: 'GET' }),
      ]);
      setUsage(usageData);
      if (user) {
        setFullName(user.full_name || '');
        setBusinessType(user.business_type || '');
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      await api.request('/api/auth/me', {
        method: 'PATCH',
        body: JSON.stringify({ full_name: fullName, business_type: businessType }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error('Failed to save profile:', err);
    } finally {
      setSaving(false);
    }
  };

  const planLabel = (plan: string) => {
    const labels: Record<string, string> = {
      trial: 'Free Trial',
      starter: 'Starter',
      growth: 'Growth',
      pro: 'Pro',
      admin: 'Admin',
    };
    return labels[plan] || plan;
  };

  const planColor = (plan: string) => {
    if (plan === 'admin') return 'bg-purple-100 text-purple-700 border-purple-200';
    if (plan === 'trial') return 'bg-gray-100 text-gray-700 border-gray-200';
    return 'bg-green-100 text-green-700 border-green-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500">Manage your account and billing</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center">
            <User className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Profile</h2>
            <p className="text-sm text-gray-500">Your personal information</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600">
              <Mail className="w-4 h-4" />
              {user?.email || '—'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
            <input
              type="text"
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              placeholder="e.g., Real Estate, E-commerce, Consulting"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent"
            />
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSaveProfile}
              disabled={saving}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            {saved && <span className="text-sm text-green-600 font-medium">Saved!</span>}
          </div>
        </div>
      </div>

      {/* Plan & Billing Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
            <CreditCard className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Plan & Billing</h2>
            <p className="text-sm text-gray-500">Your subscription and usage</p>
          </div>
        </div>

        {usage && (
          <div className="space-y-6">
            {/* Current Plan */}
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">Current Plan</div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 text-sm font-medium rounded-full border ${planColor(usage.plan)}`}>
                    {planLabel(usage.plan)}
                  </span>
                  {usage.is_trial && !usage.trial_expired && (
                    <span className="text-sm text-gray-500">
                      {usage.trial_days_left} days remaining
                    </span>
                  )}
                  {usage.is_unlimited && (
                    <span className="text-sm text-purple-600 font-medium">Unlimited access</span>
                  )}
                </div>
              </div>
              {!usage.is_unlimited && (
                <a
                  href="mailto:support@aivaro-ai.com?subject=Upgrade%20Plan"
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700"
                >
                  Upgrade Plan <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>

            {/* Usage Bars */}
            {!usage.is_unlimited && (
              <div className="space-y-4">
                {[
                  { label: 'Active Workflows', data: usage.usage.active_workflows },
                  { label: 'Total Runs', data: usage.usage.total_runs },
                  { label: 'Knowledge Entries', data: usage.usage.knowledge_entries },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-700">{item.label}</span>
                      <span className="text-sm text-gray-500">
                        {item.data.used} / {item.data.limit >= 999 ? '∞' : item.data.limit}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          item.data.limit > 0 && item.data.used / item.data.limit > 0.8
                            ? 'bg-red-500'
                            : 'bg-primary-500'
                        }`}
                        style={{
                          width: item.data.limit >= 999
                            ? '5%'
                            : `${Math.min(100, (item.data.used / Math.max(item.data.limit, 1)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Features */}
            <div className="pt-4 border-t border-gray-100">
              <div className="text-sm font-medium text-gray-700 mb-2">Features</div>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'AI Agent Tasks', enabled: usage.features.agent_tasks },
                  { label: 'File Import', enabled: usage.features.file_import },
                ].map((feat) => (
                  <div key={feat.label} className="flex items-center gap-2 text-sm">
                    <span className={`w-2 h-2 rounded-full ${feat.enabled ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span className={feat.enabled ? 'text-gray-700' : 'text-gray-400'}>{feat.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-xl border border-red-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
            <Shield className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Danger Zone</h2>
            <p className="text-sm text-gray-500">Irreversible actions</p>
          </div>
        </div>
        <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-100">
          <div>
            <div className="text-sm font-medium text-gray-900">Delete Account</div>
            <div className="text-xs text-gray-500">Permanently delete your account and all data</div>
          </div>
          <a
            href="mailto:support@aivaro-ai.com?subject=Delete%20My%20Account"
            className="px-4 py-2 text-sm font-medium text-red-700 bg-white border border-red-300 rounded-lg hover:bg-red-50"
          >
            Contact Support
          </a>
        </div>
      </div>
    </div>
  );
}

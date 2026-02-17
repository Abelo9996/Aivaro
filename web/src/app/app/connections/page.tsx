'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Key, X } from 'lucide-react';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import ServiceIcon from '@/components/ui/ServiceIcon';
import type { Connection } from '@/types';

const availableConnections = [
  // Core integrations
  { type: 'google', name: 'Google', description: 'Gmail, Google Sheets, Calendar', authType: 'oauth' },
  { type: 'stripe', name: 'Stripe', description: 'Payments and invoicing', authType: 'api_key' },
  { type: 'slack', name: 'Slack', description: 'Team messaging', authType: 'oauth' },
  { type: 'notion', name: 'Notion', description: 'Notes and databases', authType: 'oauth' },
  // Scheduling & Marketing
  { type: 'calendly', name: 'Calendly', description: 'Scheduling and bookings', authType: 'oauth' },
  { type: 'airtable', name: 'Airtable', description: 'Spreadsheets and databases', authType: 'api_key' },
  { type: 'mailchimp', name: 'Mailchimp', description: 'Email marketing', authType: 'api_key' },
  { type: 'twilio', name: 'Twilio', description: 'SMS and voice', authType: 'api_key' },
  // SMS Marketing
  { type: 'textedly', name: 'Textedly', description: 'SMS marketing platform', authType: 'api_key' },
  // CRM & Sales
  { type: 'hubspot', name: 'HubSpot', description: 'CRM and marketing automation', authType: 'oauth' },
  { type: 'salesforce', name: 'Salesforce', description: 'Enterprise CRM', authType: 'oauth' },
  // E-commerce & Finance
  { type: 'shopify', name: 'Shopify', description: 'E-commerce platform', authType: 'oauth' },
  { type: 'quickbooks', name: 'QuickBooks', description: 'Accounting and invoicing', authType: 'oauth' },
  // Website & Domain Providers
  { type: 'godaddy', name: 'GoDaddy', description: 'Domains and hosting', authType: 'api_key' },
  { type: 'wix', name: 'Wix', description: 'Website builder', authType: 'oauth' },
  { type: 'squarespace', name: 'Squarespace', description: 'Website and commerce', authType: 'oauth' },
  { type: 'webflow', name: 'Webflow', description: 'Visual web development', authType: 'api_key' },
  // No-Code Platforms
  { type: 'base44', name: 'Base44', description: 'No-code app builder', authType: 'api_key' },
  { type: 'bubble', name: 'Bubble', description: 'No-code platform', authType: 'api_key' },
  { type: 'zapier', name: 'Zapier', description: 'Workflow automation', authType: 'api_key' },
  // Analytics & Traffic
  { type: 'google_analytics', name: 'Google Analytics', description: 'Website analytics', authType: 'oauth' },
  { type: 'cloudflare', name: 'Cloudflare', description: 'CDN and security', authType: 'api_key' },
  { type: 'plausible', name: 'Plausible', description: 'Privacy-friendly analytics', authType: 'api_key' },
  { type: 'hotjar', name: 'Hotjar', description: 'Heatmaps and recordings', authType: 'api_key' },
  // Social Media
  { type: 'facebook', name: 'Facebook', description: 'Social media and ads', authType: 'oauth' },
  { type: 'instagram', name: 'Instagram', description: 'Photo and video sharing', authType: 'oauth' },
  { type: 'twitter', name: 'Twitter', description: 'Social media platform', authType: 'oauth' },
  { type: 'linkedin', name: 'LinkedIn', description: 'Professional networking', authType: 'oauth' },
  { type: 'tiktok', name: 'TikTok', description: 'Short-form video', authType: 'oauth' },
  // Developer & Project Management
  { type: 'github', name: 'GitHub', description: 'Code repositories and issues', authType: 'oauth' },
  { type: 'discord', name: 'Discord', description: 'Community chat', authType: 'oauth' },
  { type: 'asana', name: 'Asana', description: 'Project management', authType: 'oauth' },
  { type: 'trello', name: 'Trello', description: 'Kanban boards', authType: 'api_key' },
  // Support & Customer Success
  { type: 'zendesk', name: 'Zendesk', description: 'Customer support tickets', authType: 'oauth' },
  { type: 'intercom', name: 'Intercom', description: 'Customer messaging', authType: 'oauth' },
  // Issue Tracking
  { type: 'linear', name: 'Linear', description: 'Issue tracking', authType: 'oauth' },
  { type: 'jira', name: 'Jira', description: 'Project and issue tracking', authType: 'oauth' },
];

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [apiKeyModal, setApiKeyModal] = useState<{ type: string; name: string } | null>(null);
  const [apiKey, setApiKey] = useState('');
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check for OAuth callback results
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    
    if (success) {
      setMessage({ type: 'success', text: `Successfully connected to ${success}!` });
      // Clear the URL params
      window.history.replaceState({}, '', '/app/connections');
    } else if (error) {
      setMessage({ type: 'error', text: `Connection failed: ${error}` });
      window.history.replaceState({}, '', '/app/connections');
    }
    
    loadConnections();
  }, [searchParams]);

  const loadConnections = async () => {
    try {
      const data = await api.getConnections();
      setConnections(data);
    } catch (err) {
      console.error('Failed to load connections:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (type: string) => {
    const service = availableConnections.find(s => s.type === type);
    
    // For API key auth types, show the modal
    if (service?.authType === 'api_key') {
      setApiKeyModal({ type, name: service.name });
      setApiKey('');
      return;
    }
    
    // For OAuth, proceed with the existing flow
    setConnecting(type);
    setMessage(null);
    
    try {
      // First try OAuth flow
      const response = await api.authorizeConnection(type);
      
      if (response.authorization_url) {
        // Redirect to OAuth provider
        window.location.href = response.authorization_url;
      } else if (response.demo_mode) {
        // OAuth not configured, use demo mode
        await api.createConnection({
          name: type.charAt(0).toUpperCase() + type.slice(1),
          type: type,
          credentials: { demo: true },
        });
        setMessage({ 
          type: 'success', 
          text: `${type} connected in demo mode. Configure OAuth credentials for real integration.` 
        });
        loadConnections();
      }
    } catch (err: any) {
      console.error('Failed to connect:', err);
      setMessage({ type: 'error', text: err.message || 'Failed to connect' });
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (id: string) => {
    if (!confirm('Are you sure you want to disconnect this service?')) return;
    
    try {
      await api.deleteConnection(id);
      setMessage({ type: 'success', text: 'Connection removed successfully' });
      loadConnections();
    } catch (err) {
      console.error('Failed to disconnect:', err);
    }
  };

  const handleApiKeySubmit = async () => {
    if (!apiKeyModal || !apiKey.trim()) return;
    
    setConnecting(apiKeyModal.type);
    setMessage(null);
    
    try {
      await api.createConnection({
        name: apiKeyModal.name,
        type: apiKeyModal.type,
        credentials: { api_key: apiKey.trim() },
      });
      setMessage({ 
        type: 'success', 
        text: `${apiKeyModal.name} connected successfully!` 
      });
      setApiKeyModal(null);
      setApiKey('');
      loadConnections();
    } catch (err: any) {
      console.error('Failed to connect:', err);
      setMessage({ type: 'error', text: err.message || 'Failed to connect' });
    } finally {
      setConnecting(null);
    }
  };

  const getApiKeyPlaceholder = (type: string) => {
    switch (type) {
      case 'stripe':
        return 'sk_live_... or sk_test_...';
      case 'airtable':
        return 'pat... or key...';
      case 'mailchimp':
        return 'Your Mailchimp API key';
      case 'twilio':
        return 'Your Twilio Auth Token';
      case 'textedly':
        return 'Your Textedly API key';
      case 'godaddy':
        return 'Your GoDaddy API key';
      case 'webflow':
        return 'Your Webflow API token';
      case 'base44':
        return 'Your Base44 API key';
      case 'bubble':
        return 'Your Bubble API token';
      case 'zapier':
        return 'Your Zapier webhook key';
      case 'cloudflare':
        return 'Your Cloudflare API token';
      case 'plausible':
        return 'Your Plausible API key';
      case 'hotjar':
        return 'Your Hotjar API key';
      case 'trello':
        return 'Your Trello API key';
      default:
        return 'Enter your API key';
    }
  };

  const getApiKeyInstructions = (type: string) => {
    switch (type) {
      case 'stripe':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Find your API key in{' '}
            <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Stripe Dashboard → Developers → API keys
            </a>
          </p>
        );
      case 'airtable':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Generate a token at{' '}
            <a href="https://airtable.com/create/tokens" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Airtable → Account → Developer hub
            </a>
          </p>
        );
      case 'textedly':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Find your API key in{' '}
            <a href="https://www.textedly.com/api" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Textedly Dashboard → API Settings
            </a>
          </p>
        );
      case 'godaddy':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Generate API key at{' '}
            <a href="https://developer.godaddy.com/keys" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              GoDaddy Developer Portal → API Keys
            </a>
          </p>
        );
      case 'webflow':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Generate a token at{' '}
            <a href="https://webflow.com/dashboard/account/integrations" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Webflow → Account → Integrations
            </a>
          </p>
        );
      case 'cloudflare':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Create an API token at{' '}
            <a href="https://dash.cloudflare.com/profile/api-tokens" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Cloudflare Dashboard → API Tokens
            </a>
          </p>
        );
      case 'plausible':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Generate API key at{' '}
            <a href="https://plausible.io/settings" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Plausible → Settings → API Keys
            </a>
          </p>
        );
      case 'hotjar':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Find your Site ID in{' '}
            <a href="https://insights.hotjar.com/site/list" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Hotjar → Sites & Organizations
            </a>
          </p>
        );
      default:
        return null;
    }
  };

  const getConnectionByType = (type: string) => {
    return connections.find((c: Connection) => c.type === type);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading connections...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Connections</h1>
        <p className="text-gray-500">
          Connect your apps to use them in your workflows
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-700' 
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      <div data-walkthrough="connections-grid" className="grid md:grid-cols-2 gap-4">
        {availableConnections.map((service) => {
          const connected = getConnectionByType(service.type);
          const isConnecting = connecting === service.type;
          
          return (
            <div
              key={service.type}
              className={`bg-white rounded-xl border p-6 ${
                connected ? 'border-green-200 bg-green-50/30' : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 flex items-center justify-center">
                    <ServiceIcon type={service.type} size={40} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{service.name}</h3>
                      {connected && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                          Connected
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{service.description}</p>
                    {connected && (
                      <p className="text-xs text-gray-400 mt-1">
                        Connected {formatDate(connected.created_at)}
                      </p>
                    )}
                  </div>
                </div>
                <div>
                  {connected ? (
                    <button
                      onClick={() => handleDisconnect(connected.id)}
                      className="text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                      Disconnect
                    </button>
                  ) : (
                    <button
                      onClick={() => handleConnect(service.type)}
                      disabled={isConnecting}
                      className="bg-primary-600 text-white px-4 py-2 text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isConnecting ? 'Connecting...' : 'Connect'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Info */}
      <div className="mt-8 bg-gray-50 rounded-xl p-6">
        <h3 className="font-semibold mb-2">🔒 Your data is secure</h3>
        <p className="text-sm text-gray-600">
          We use OAuth to connect to your apps, which means we never store your
          passwords. You can revoke access at any time from the app's settings
          or from this page.
        </p>
      </div>

      {/* API Key Modal */}
      {apiKeyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <ServiceIcon type={apiKeyModal.type} size={32} />
                <h2 className="text-lg font-semibold">Connect {apiKeyModal.name}</h2>
              </div>
              <button
                onClick={() => {
                  setApiKeyModal(null);
                  setApiKey('');
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="p-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Key className="w-4 h-4 inline mr-1" />
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={getApiKeyPlaceholder(apiKeyModal.type)}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                autoFocus
              />
              {getApiKeyInstructions(apiKeyModal.type)}
              
              <div className="mt-6 flex gap-3">
                <button
                  onClick={() => {
                    setApiKeyModal(null);
                    setApiKey('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 transition font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleApiKeySubmit}
                  disabled={!apiKey.trim() || connecting === apiKeyModal.type}
                  className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {connecting === apiKeyModal.type ? 'Connecting...' : 'Connect'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

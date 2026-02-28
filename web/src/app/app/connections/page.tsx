'use client';

import { useEffect, useState, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { Key, X, Search, Filter } from 'lucide-react';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import ServiceIcon from '@/components/ui/ServiceIcon';
import type { Connection } from '@/types';

// Category definitions
const categories = [
  { id: 'all', label: 'All', icon: '🔗' },
  { id: 'connected', label: 'Connected', icon: '✅' },
  { id: 'core', label: 'Core', icon: '⚡' },
  { id: 'communication', label: 'Communication', icon: '💬' },
  { id: 'productivity', label: 'Productivity', icon: '📋' },
];

const availableConnections = [
  // Core integrations
  {
    type: 'google',
    name: 'Google',
    description: 'Send emails via Gmail, read inbox, create calendar events, append rows to Sheets, look up spreadsheets by name',
    authType: 'oauth',
    category: 'core',
  },
  {
    type: 'stripe',
    name: 'Stripe',
    description: 'Create payment links, send invoices, look up customers, check payment status',
    authType: 'api_key',
    category: 'core',
  },
  {
    type: 'twilio',
    name: 'Twilio',
    description: 'Send SMS messages, send WhatsApp messages, make voice calls with text-to-speech',
    authType: 'api_key',
    category: 'communication',
  },
  {
    type: 'slack',
    name: 'Slack',
    description: 'Send messages to channels, post notifications to your team',
    authType: 'oauth',
    category: 'communication',
  },
  {
    type: 'airtable',
    name: 'Airtable',
    description: 'Create, update, list, and search records in Airtable bases',
    authType: 'api_key',
    category: 'productivity',
  },
  {
    type: 'notion',
    name: 'Notion',
    description: 'Create and update pages, query databases, search across your workspace',
    authType: 'oauth',
    category: 'productivity',
  },
  {
    type: 'calendly',
    name: 'Calendly',
    description: 'List scheduled events, get event details, cancel events, create scheduling links',
    authType: 'oauth',
    category: 'productivity',
  },
  {
    type: 'mailchimp',
    name: 'Mailchimp',
    description: 'Add and update subscribers, tag contacts, send email campaigns',
    authType: 'api_key',
    category: 'communication',
  },
];

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [apiKeyModal, setApiKeyModal] = useState<{ type: string; name: string } | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [disconnectTarget, setDisconnectTarget] = useState<string | null>(null);
  const searchParams = useSearchParams();

  // Filter connections based on search and category
  const filteredConnections = useMemo(() => {
    return availableConnections.filter((service) => {
      // Search filter
      const matchesSearch = searchQuery === '' || 
        service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        service.description.toLowerCase().includes(searchQuery.toLowerCase());
      
      // Category filter
      let matchesCategory = true;
      if (selectedCategory === 'connected') {
        matchesCategory = connections.some((c: Connection) => c.type === service.type);
      } else if (selectedCategory !== 'all') {
        matchesCategory = service.category === selectedCategory;
      }
      
      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory, connections]);

  // Count connections per category
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: availableConnections.length, connected: connections.length };
    availableConnections.forEach((service) => {
      counts[service.category] = (counts[service.category] || 0) + 1;
    });
    return counts;
  }, [connections]);

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
    setDisconnectTarget(id);
  };

  const confirmDisconnect = async () => {
    if (!disconnectTarget) return;
    try {
      await api.deleteConnection(disconnectTarget);
      setMessage({ type: 'success', text: 'Connection removed successfully' });
      loadConnections();
    } catch (err) {
      console.error('Failed to disconnect:', err);
    } finally {
      setDisconnectTarget(null);
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
        return 'Your Mailchimp API key (e.g. abc123-us21)';
      case 'twilio':
        return 'Account SID and Auth Token (comma-separated)';
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
            </a>. Use your Secret key (starts with sk_).
          </p>
        );
      case 'airtable':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Generate a personal access token at{' '}
            <a href="https://airtable.com/create/tokens" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Airtable → Account → Developer hub
            </a>. Grant access to the bases you want to use.
          </p>
        );
      case 'mailchimp':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Find your API key at{' '}
            <a href="https://us1.admin.mailchimp.com/account/api/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Mailchimp → Account → Extras → API keys
            </a>. The key includes your data center (e.g. -us21).
          </p>
        );
      case 'twilio':
        return (
          <p className="text-sm text-gray-500 mt-2">
            Find your Account SID and Auth Token at{' '}
            <a href="https://console.twilio.com/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
              Twilio Console → Account Info
            </a>. Enter as: ACCOUNT_SID,AUTH_TOKEN
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
      <div className="mb-6">
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

      {/* Search and Filter Bar */}
      <div className="mb-6 space-y-4">
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search connections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                selectedCategory === category.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <span className="mr-1">{category.icon}</span>
              {category.label}
              <span className={`ml-1.5 text-xs ${
                selectedCategory === category.id ? 'text-white/80' : 'text-gray-400'
              }`}>
                {categoryCounts[category.id] || 0}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Results Info */}
      <div className="mb-4 text-sm text-gray-500">
        Showing {filteredConnections.length} of {availableConnections.length} integrations
        {searchQuery && <span> matching &ldquo;{searchQuery}&rdquo;</span>}
      </div>

      {/* Connections Grid */}
      {filteredConnections.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <Filter className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No connections match your filters</p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}
            className="mt-2 text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div data-walkthrough="connections-grid" className="grid md:grid-cols-2 gap-4">
          {filteredConnections.map((service) => {
            const connected = getConnectionByType(service.type);
            const isConnecting = connecting === service.type;
            
            return (
              <div
                key={service.type}
                className={`bg-white rounded-xl border p-6 transition-all hover:shadow-md ${
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
      )}

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

      <ConfirmDialog
        open={!!disconnectTarget}
        title="Disconnect service"
        message="This will remove the connection. Any workflows using this service will stop working until you reconnect."
        confirmLabel="Disconnect"
        onConfirm={confirmDisconnect}
        onCancel={() => setDisconnectTarget(null)}
      />
    </div>
  );
}

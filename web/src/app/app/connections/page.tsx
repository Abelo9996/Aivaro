'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Connection } from '@/types';

const availableConnections = [
  { type: 'google', name: 'Google', icon: '📧', description: 'Gmail, Google Sheets, Calendar' },
  { type: 'stripe', name: 'Stripe', icon: '💳', description: 'Payments and invoicing' },
  { type: 'slack', name: 'Slack', icon: '💬', description: 'Team messaging' },
  { type: 'notion', name: 'Notion', icon: '📝', description: 'Notes and databases' },
  { type: 'calendly', name: 'Calendly', icon: '📅', description: 'Scheduling and bookings' },
  { type: 'airtable', name: 'Airtable', icon: '📊', description: 'Spreadsheets and databases' },
  { type: 'mailchimp', name: 'Mailchimp', icon: '✉️', description: 'Email marketing' },
  { type: 'twilio', name: 'Twilio', icon: '📱', description: 'SMS and voice' },
];

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
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
                  <div className="text-3xl">{service.icon}</div>
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

      {/* Setup Instructions */}
      <div className="mt-4 bg-blue-50 rounded-xl p-6">
        <h3 className="font-semibold mb-2 text-blue-900">🔧 Setting up OAuth</h3>
        <p className="text-sm text-blue-800 mb-3">
          To enable real OAuth connections, set these environment variables in your API:
        </p>
        <div className="bg-blue-100 rounded-lg p-3 font-mono text-xs text-blue-900">
          <div>GOOGLE_CLIENT_ID=your_client_id</div>
          <div>GOOGLE_CLIENT_SECRET=your_client_secret</div>
          <div className="mt-2">SLACK_CLIENT_ID=your_client_id</div>
          <div>SLACK_CLIENT_SECRET=your_client_secret</div>
        </div>
        <p className="text-sm text-blue-700 mt-3">
          Get these from{' '}
          <a href="https://console.cloud.google.com/apis/credentials" target="_blank" className="underline">
            Google Cloud Console
          </a>{' '}
          or{' '}
          <a href="https://api.slack.com/apps" target="_blank" className="underline">
            Slack API
          </a>
        </p>
      </div>
    </div>
  );
}

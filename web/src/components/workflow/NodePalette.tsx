'use client';

import { useState, useMemo } from 'react';
import { Search, X } from 'lucide-react';
import ServiceIcon from '@/components/ui/ServiceIcon';

interface NodePaletteProps {
  onClose: () => void;
  onAddNode: (type: string, nodeType: string, label: string) => void;
  isAdvancedMode: boolean;
}

interface NodeItem {
  type: string;
  nodeType: string;
  label: string;
}

interface NodeCategory {
  category: string;
  provider?: string;
  items: NodeItem[];
}

const allNodes: NodeCategory[] = [
  {
    category: 'Triggers',
    items: [
      { type: 'trigger', nodeType: 'start_form', label: 'Form Submitted' },
      { type: 'trigger', nodeType: 'start_schedule', label: 'On a Schedule' },
      { type: 'trigger', nodeType: 'start_email', label: 'Email Received' },
      { type: 'trigger', nodeType: 'start_manual', label: 'Manual Start' },
      { type: 'trigger', nodeType: 'start_webhook', label: 'Webhook' },
    ],
  },
  {
    category: 'AI',
    items: [
      { type: 'action', nodeType: 'ai_reply', label: 'AI Reply' },
      { type: 'action', nodeType: 'ai_summarize', label: 'AI Summarize' },
      { type: 'action', nodeType: 'ai_extract', label: 'AI Extract Data' },
      { type: 'action', nodeType: 'email_template', label: 'Email Template' },
    ],
  },
  {
    category: 'Logic',
    items: [
      { type: 'condition', nodeType: 'condition', label: 'If/Else' },
      { type: 'approval', nodeType: 'approval', label: 'Wait for Approval' },
      { type: 'action', nodeType: 'delay', label: 'Wait / Delay' },
      { type: 'action', nodeType: 'transform', label: 'Transform Data' },
      { type: 'action', nodeType: 'http_request', label: 'HTTP Request' },
    ],
  },
  {
    category: 'Email',
    items: [
      { type: 'action', nodeType: 'send_email', label: 'Send Email (Gmail)' },
      { type: 'action', nodeType: 'send_notification', label: 'Send Notification' },
    ],
  },
  {
    category: 'Google',
    provider: 'google',
    items: [
      { type: 'action', nodeType: 'google_calendar_create', label: 'Create Calendar Event' },
      { type: 'action', nodeType: 'append_row', label: 'Add to Spreadsheet' },
      { type: 'action', nodeType: 'read_sheet', label: 'Read Spreadsheet' },
      { type: 'action', nodeType: 'google_calendar_list', label: 'List Calendar Events' },
      { type: 'action', nodeType: 'google_calendar_update', label: 'Update Calendar Event' },
      { type: 'action', nodeType: 'google_calendar_delete', label: 'Delete Calendar Event' },
      { type: 'action', nodeType: 'google_contacts_create', label: 'Create Contact' },
      { type: 'action', nodeType: 'google_contacts_search', label: 'Search Contacts' },
      { type: 'action', nodeType: 'google_drive_list', label: 'List Drive Files' },
      { type: 'action', nodeType: 'google_drive_upload', label: 'Upload to Drive' },
    ],
  },
  {
    category: 'Slack',
    provider: 'slack',
    items: [
      { type: 'action', nodeType: 'send_slack', label: 'Send Channel Message' },
      { type: 'action', nodeType: 'slack_send_dm', label: 'Send Direct Message' },
      { type: 'action', nodeType: 'slack_create_channel', label: 'Create Channel' },
      { type: 'action', nodeType: 'slack_list_channels', label: 'List Channels' },
      { type: 'action', nodeType: 'slack_list_users', label: 'List Users' },
      { type: 'action', nodeType: 'slack_set_topic', label: 'Set Channel Topic' },
      { type: 'action', nodeType: 'slack_add_reaction', label: 'Add Reaction' },
    ],
  },
  {
    category: 'Stripe',
    provider: 'stripe',
    items: [
      { type: 'action', nodeType: 'stripe_create_payment_link', label: 'Create Payment Link' },
      { type: 'action', nodeType: 'stripe_create_invoice', label: 'Create Invoice' },
      { type: 'action', nodeType: 'stripe_send_invoice', label: 'Send Invoice' },
      { type: 'action', nodeType: 'stripe_check_payment', label: 'Check Payment Status' },
      { type: 'action', nodeType: 'stripe_get_customer', label: 'Get/Create Customer' },
      { type: 'action', nodeType: 'stripe_list_payments', label: 'List Payments' },
      { type: 'action', nodeType: 'stripe_create_subscription', label: 'Create Subscription' },
      { type: 'action', nodeType: 'stripe_refund', label: 'Create Refund' },
    ],
  },
  {
    category: 'Twilio',
    provider: 'twilio',
    items: [
      { type: 'action', nodeType: 'twilio_send_sms', label: 'Send SMS' },
      { type: 'action', nodeType: 'twilio_send_whatsapp', label: 'Send WhatsApp' },
      { type: 'action', nodeType: 'twilio_make_call', label: 'Make Phone Call' },
      { type: 'action', nodeType: 'twilio_send_mms', label: 'Send MMS' },
      { type: 'action', nodeType: 'twilio_list_messages', label: 'List Messages' },
      { type: 'action', nodeType: 'twilio_lookup', label: 'Phone Number Lookup' },
    ],
  },
  {
    category: 'Airtable',
    provider: 'airtable',
    items: [
      { type: 'action', nodeType: 'airtable_create_record', label: 'Create Record' },
      { type: 'action', nodeType: 'airtable_update_record', label: 'Update Record' },
      { type: 'action', nodeType: 'airtable_list_records', label: 'List Records' },
      { type: 'action', nodeType: 'airtable_find_record', label: 'Find Record' },
      { type: 'action', nodeType: 'airtable_delete_record', label: 'Delete Record' },
      { type: 'action', nodeType: 'airtable_list_bases', label: 'List Bases' },
      { type: 'action', nodeType: 'airtable_list_tables', label: 'List Tables' },
    ],
  },
  {
    category: 'Notion',
    provider: 'notion',
    items: [
      { type: 'action', nodeType: 'notion_create_page', label: 'Create Page' },
      { type: 'action', nodeType: 'notion_update_page', label: 'Update Page' },
      { type: 'action', nodeType: 'notion_query_database', label: 'Query Database' },
      { type: 'action', nodeType: 'notion_search', label: 'Search' },
      { type: 'action', nodeType: 'notion_create_database', label: 'Create Database' },
      { type: 'action', nodeType: 'notion_get_page', label: 'Get Page' },
      { type: 'action', nodeType: 'notion_delete_page', label: 'Archive Page' },
    ],
  },
  {
    category: 'Calendly',
    provider: 'calendly',
    items: [
      { type: 'action', nodeType: 'calendly_list_events', label: 'List Events' },
      { type: 'action', nodeType: 'calendly_create_link', label: 'Create Scheduling Link' },
      { type: 'action', nodeType: 'calendly_get_event', label: 'Get Event Details' },
      { type: 'action', nodeType: 'calendly_cancel_event', label: 'Cancel Event' },
      { type: 'action', nodeType: 'calendly_list_event_types', label: 'List Event Types' },
    ],
  },
  {
    category: 'Mailchimp',
    provider: 'mailchimp',
    items: [
      { type: 'action', nodeType: 'mailchimp_add_subscriber', label: 'Add Subscriber' },
      { type: 'action', nodeType: 'mailchimp_update_subscriber', label: 'Update Subscriber' },
      { type: 'action', nodeType: 'mailchimp_add_tags', label: 'Add Tags' },
      { type: 'action', nodeType: 'mailchimp_send_campaign', label: 'Send Campaign' },
      { type: 'action', nodeType: 'mailchimp_create_campaign', label: 'Create Campaign' },
      { type: 'action', nodeType: 'mailchimp_list_audiences', label: 'List Audiences' },
      { type: 'action', nodeType: 'mailchimp_list_campaigns', label: 'List Campaigns' },
    ],
  },
  {
    category: 'HubSpot',
    provider: 'hubspot',
    items: [
      { type: 'action', nodeType: 'hubspot_create_contact', label: 'Create Contact' },
      { type: 'action', nodeType: 'hubspot_update_contact', label: 'Update Contact' },
      { type: 'action', nodeType: 'hubspot_search_contacts', label: 'Search Contacts' },
      { type: 'action', nodeType: 'hubspot_create_deal', label: 'Create Deal' },
      { type: 'action', nodeType: 'hubspot_update_deal', label: 'Update Deal' },
      { type: 'action', nodeType: 'hubspot_list_deals', label: 'List Deals' },
      { type: 'action', nodeType: 'hubspot_create_company', label: 'Create Company' },
      { type: 'action', nodeType: 'hubspot_create_ticket', label: 'Create Ticket' },
      { type: 'action', nodeType: 'hubspot_send_email', label: 'Send Email' },
      { type: 'action', nodeType: 'hubspot_create_note', label: 'Create Note' },
    ],
  },
  {
    category: 'Shopify',
    provider: 'shopify',
    items: [
      { type: 'action', nodeType: 'shopify_list_orders', label: 'List Orders' },
      { type: 'action', nodeType: 'shopify_get_order', label: 'Get Order' },
      { type: 'action', nodeType: 'shopify_create_product', label: 'Create Product' },
      { type: 'action', nodeType: 'shopify_update_product', label: 'Update Product' },
      { type: 'action', nodeType: 'shopify_list_products', label: 'List Products' },
      { type: 'action', nodeType: 'shopify_list_customers', label: 'List Customers' },
      { type: 'action', nodeType: 'shopify_create_customer', label: 'Create Customer' },
      { type: 'action', nodeType: 'shopify_create_discount', label: 'Create Discount' },
      { type: 'action', nodeType: 'shopify_fulfill_order', label: 'Fulfill Order' },
    ],
  },
  {
    category: 'Discord',
    provider: 'discord',
    items: [
      { type: 'action', nodeType: 'discord_send_message', label: 'Send Message' },
      { type: 'action', nodeType: 'discord_create_channel', label: 'Create Channel' },
      { type: 'action', nodeType: 'discord_list_channels', label: 'List Channels' },
      { type: 'action', nodeType: 'discord_list_members', label: 'List Members' },
      { type: 'action', nodeType: 'discord_create_role', label: 'Create Role' },
      { type: 'action', nodeType: 'discord_add_reaction', label: 'Add Reaction' },
    ],
  },
  {
    category: 'Jira',
    provider: 'jira',
    items: [
      { type: 'action', nodeType: 'jira_create_issue', label: 'Create Issue' },
      { type: 'action', nodeType: 'jira_update_issue', label: 'Update Issue' },
      { type: 'action', nodeType: 'jira_search_issues', label: 'Search Issues' },
      { type: 'action', nodeType: 'jira_get_issue', label: 'Get Issue' },
      { type: 'action', nodeType: 'jira_add_comment', label: 'Add Comment' },
      { type: 'action', nodeType: 'jira_transition_issue', label: 'Transition Issue' },
      { type: 'action', nodeType: 'jira_list_projects', label: 'List Projects' },
    ],
  },
  {
    category: 'GitHub',
    provider: 'github',
    items: [
      { type: 'action', nodeType: 'github_create_issue', label: 'Create Issue' },
      { type: 'action', nodeType: 'github_list_repos', label: 'List Repositories' },
      { type: 'action', nodeType: 'github_create_pr', label: 'Create Pull Request' },
      { type: 'action', nodeType: 'github_list_issues', label: 'List Issues' },
      { type: 'action', nodeType: 'github_get_repo', label: 'Get Repository' },
      { type: 'action', nodeType: 'github_add_comment', label: 'Add Comment' },
      { type: 'action', nodeType: 'github_create_repo', label: 'Create Repository' },
    ],
  },
  {
    category: 'Linear',
    provider: 'linear',
    items: [
      { type: 'action', nodeType: 'linear_create_issue', label: 'Create Issue' },
      { type: 'action', nodeType: 'linear_update_issue', label: 'Update Issue' },
      { type: 'action', nodeType: 'linear_list_issues', label: 'List Issues' },
      { type: 'action', nodeType: 'linear_list_projects', label: 'List Projects' },
      { type: 'action', nodeType: 'linear_list_teams', label: 'List Teams' },
      { type: 'action', nodeType: 'linear_add_comment', label: 'Add Comment' },
    ],
  },
  {
    category: 'Monday',
    provider: 'monday',
    items: [
      { type: 'action', nodeType: 'monday_create_item', label: 'Create Item' },
      { type: 'action', nodeType: 'monday_update_item', label: 'Update Item' },
      { type: 'action', nodeType: 'monday_list_items', label: 'List Items' },
      { type: 'action', nodeType: 'monday_list_boards', label: 'List Boards' },
      { type: 'action', nodeType: 'monday_create_update', label: 'Add Update' },
    ],
  },
  {
    category: 'SendGrid',
    provider: 'sendgrid',
    items: [
      { type: 'action', nodeType: 'sendgrid_send_email', label: 'Send Email' },
      { type: 'action', nodeType: 'sendgrid_add_contact', label: 'Add Contact' },
      { type: 'action', nodeType: 'sendgrid_list_contacts', label: 'List Contacts' },
      { type: 'action', nodeType: 'sendgrid_create_list', label: 'Create List' },
    ],
  },
  {
    category: 'WhatsApp (Cloud API)',
    provider: 'whatsapp',
    items: [
      { type: 'action', nodeType: 'whatsapp_send_message', label: 'Send Message' },
      { type: 'action', nodeType: 'whatsapp_send_template', label: 'Send Template Message' },
      { type: 'action', nodeType: 'whatsapp_send_media', label: 'Send Media' },
    ],
  },
  {
    category: 'Brevo',
    provider: 'brevo',
    items: [
      { type: 'action', nodeType: 'brevo_send_email', label: 'Send Transactional Email' },
      { type: 'action', nodeType: 'brevo_send_sms', label: 'Send SMS' },
      { type: 'action', nodeType: 'brevo_create_contact', label: 'Create Contact' },
      { type: 'action', nodeType: 'brevo_update_contact', label: 'Update Contact' },
      { type: 'action', nodeType: 'brevo_list_contacts', label: 'List Contacts' },
      { type: 'action', nodeType: 'brevo_send_whatsapp', label: 'Send WhatsApp' },
      { type: 'action', nodeType: 'brevo_send_campaign', label: 'Send Campaign' },
    ],
  },
];

// Simple mode: only show the most commonly used nodes
const simpleCategories = new Set([
  'Triggers', 'AI', 'Logic', 'Email', 'Google', 'Slack', 'Stripe',
  'Twilio', 'Airtable', 'Notion', 'Calendly', 'Mailchimp',
]);

const simpleMaxItems: Record<string, number> = {
  'Google': 4,
  'Slack': 3,
  'Stripe': 5,
  'Twilio': 3,
  'Airtable': 4,
  'Notion': 3,
  'Calendly': 3,
  'Mailchimp': 3,
};

export default function NodePalette({
  onClose,
  onAddNode,
  isAdvancedMode,
}: NodePaletteProps) {
  const [search, setSearch] = useState('');
  const [providerFilter, setProviderFilter] = useState<string | null>(null);

  const filteredNodes = useMemo(() => {
    let categories = allNodes;

    // In simple mode, filter to common categories with limited items
    if (!isAdvancedMode && !search && !providerFilter) {
      categories = categories
        .filter(c => simpleCategories.has(c.category))
        .map(c => {
          const max = simpleMaxItems[c.category];
          if (max) return { ...c, items: c.items.slice(0, max) };
          return c;
        });
    }

    // Provider filter
    if (providerFilter) {
      categories = categories.filter(c => c.provider === providerFilter);
    }

    // Search filter
    if (search.trim()) {
      const q = search.toLowerCase();
      categories = categories
        .map(c => ({
          ...c,
          items: c.items.filter(
            item =>
              item.label.toLowerCase().includes(q) ||
              item.nodeType.toLowerCase().includes(q) ||
              c.category.toLowerCase().includes(q)
          ),
        }))
        .filter(c => c.items.length > 0);
    }

    return categories;
  }, [search, providerFilter, isAdvancedMode]);

  const providers = allNodes
    .filter(c => c.provider)
    .map(c => ({ id: c.provider!, label: c.category }));

  return (
    <div className="absolute top-16 left-4 w-80 bg-white rounded-xl border border-gray-200 shadow-xl z-10 max-h-[80vh] flex flex-col">
      <div className="sticky top-0 bg-white border-b border-gray-100 px-4 py-3 space-y-2 flex-shrink-0">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Add a Step</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setProviderFilter(null); }}
            placeholder="Search tools..."
            autoFocus
            className="w-full pl-8 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent"
          />
        </div>
        {!search && (
          <div className="flex flex-wrap gap-1">
            <button
              onClick={() => setProviderFilter(null)}
              className={`px-2 py-0.5 text-xs rounded-full transition ${
                !providerFilter ? 'bg-primary-100 text-primary-700 font-medium' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            {providers.map(p => (
              <button
                key={p.id}
                onClick={() => setProviderFilter(providerFilter === p.id ? null : p.id)}
                className={`px-2 py-0.5 text-xs rounded-full transition ${
                  providerFilter === p.id ? 'bg-primary-100 text-primary-700 font-medium' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-3">
        {filteredNodes.length === 0 ? (
          <div className="text-center text-sm text-gray-400 py-8">
            No tools found for &ldquo;{search}&rdquo;
          </div>
        ) : (
          filteredNodes.map((category) => (
            <div key={category.category} className="mb-4">
              <div className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2 px-2">
                {category.category}
              </div>
              <div className="space-y-0.5">
                {category.items.map((item) => (
                  <button
                    key={item.nodeType}
                    onClick={() => onAddNode(item.type, item.nodeType, item.label)}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left transition"
                  >
                    <ServiceIcon type={item.nodeType} size={20} />
                    <span className="text-sm">{item.label}</span>
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
        {!isAdvancedMode && !search && !providerFilter && (
          <div className="text-center text-xs text-gray-400 py-2">
            Toggle Advanced mode to see all {allNodes.reduce((n, c) => n + c.items.length, 0)} tools
          </div>
        )}
      </div>
    </div>
  );
}

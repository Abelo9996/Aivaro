'use client';

import Image from 'next/image';

// Map of service/node types to their icons
const iconMap: Record<string, { src: string; color?: string }> = {
  // Services/Integrations
  google: { src: '/icons/google.svg' },
  gmail: { src: '/icons/gmail.svg' },
  sheets: { src: '/icons/sheets.svg' },
  calendar: { src: '/icons/calendar.svg' },
  slack: { src: '/icons/slack.svg' },
  stripe: { src: '/icons/stripe.svg' },
  notion: { src: '/icons/notion.svg' },
  calendly: { src: '/icons/calendly.svg' },
  airtable: { src: '/icons/airtable.svg' },
  mailchimp: { src: '/icons/mailchimp.svg' },
  twilio: { src: '/icons/twilio.svg' },
  github: { src: '/icons/github.svg' },
  shopify: { src: '/icons/shopify.svg' },
  hubspot: { src: '/icons/hubspot.svg' },
  salesforce: { src: '/icons/salesforce.svg' },
  openai: { src: '/icons/openai.svg' },
  quickbooks: { src: '/icons/quickbooks.svg' },
  discord: { src: '/icons/discord.svg' },
  asana: { src: '/icons/asana.svg' },
  trello: { src: '/icons/trello.svg' },
  zendesk: { src: '/icons/zendesk.svg' },
  intercom: { src: '/icons/intercom.svg' },
  linear: { src: '/icons/linear.svg' },
  jira: { src: '/icons/jira.svg' },
  
  // Workflow node types - map to appropriate service icons
  start_email: { src: '/icons/gmail.svg' },
  send_email: { src: '/icons/gmail.svg' },
  append_row: { src: '/icons/sheets.svg' },
  read_sheet: { src: '/icons/sheets.svg' },
  send_slack: { src: '/icons/slack.svg' },
  ai_reply: { src: '/icons/openai.svg' },
  ai_summarize: { src: '/icons/openai.svg' },
  ai_extract: { src: '/icons/openai.svg' },
  
  // Stripe node types
  stripe_create_invoice: { src: '/icons/stripe.svg' },
  stripe_send_invoice: { src: '/icons/stripe.svg' },
  stripe_create_payment_link: { src: '/icons/stripe.svg' },
  stripe_get_customer: { src: '/icons/stripe.svg' },
  stripe_check_payment: { src: '/icons/stripe.svg' },
  
  // Google Calendar node types
  google_calendar_create: { src: '/icons/calendar.svg' },
  
  // Notion node types
  notion_create_page: { src: '/icons/notion.svg' },
  notion_update_page: { src: '/icons/notion.svg' },
  notion_query_database: { src: '/icons/notion.svg' },
  notion_search: { src: '/icons/notion.svg' },
  
  // Airtable node types
  airtable_create_record: { src: '/icons/airtable.svg' },
  airtable_update_record: { src: '/icons/airtable.svg' },
  airtable_list_records: { src: '/icons/airtable.svg' },
  airtable_find_record: { src: '/icons/airtable.svg' },
  
  // Calendly node types
  calendly_list_events: { src: '/icons/calendly.svg' },
  calendly_get_event: { src: '/icons/calendly.svg' },
  calendly_cancel_event: { src: '/icons/calendly.svg' },
  calendly_create_link: { src: '/icons/calendly.svg' },
  
  // Mailchimp node types
  mailchimp_add_subscriber: { src: '/icons/mailchimp.svg' },
  mailchimp_update_subscriber: { src: '/icons/mailchimp.svg' },
  mailchimp_add_tags: { src: '/icons/mailchimp.svg' },
  mailchimp_send_campaign: { src: '/icons/mailchimp.svg' },
  
  // Twilio node types
  twilio_send_sms: { src: '/icons/twilio.svg' },
  twilio_send_whatsapp: { src: '/icons/twilio.svg' },
  twilio_make_call: { src: '/icons/twilio.svg' },
};

// Fallback emoji icons for types without SVG icons
const emojiMap: Record<string, string> = {
  start_manual: '▶️',
  start_form: '📝',
  start_schedule: '⏰',
  start_webhook: '🔗',
  delay: '⏳',
  send_notification: '🔔',
  http_request: '🌐',
  condition: '🔀',
  transform: '🔄',
  approval: '✋',
};

interface ServiceIconProps {
  type: string;
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}

export default function ServiceIcon({ type, size = 24, className = '', style }: ServiceIconProps) {
  const normalizedType = type.toLowerCase();
  const iconInfo = iconMap[normalizedType];
  
  if (iconInfo) {
    return (
      <Image
        src={iconInfo.src}
        alt={type}
        width={size}
        height={size}
        className={className}
        style={{ objectFit: 'contain', ...style }}
      />
    );
  }
  
  // Fallback to emoji
  const emoji = emojiMap[normalizedType] || '⚡';
  return (
    <span 
      className={className}
      style={{ 
        fontSize: size * 0.8, 
        lineHeight: 1,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: size,
        height: size,
        ...style 
      }}
    >
      {emoji}
    </span>
  );
}

// Export the icon and emoji maps for use in other components
export { iconMap, emojiMap };

// Helper function to check if a type has an SVG icon
export function hasIcon(type: string): boolean {
  return type.toLowerCase() in iconMap;
}

// Get icon source or emoji for a type
export function getIconOrEmoji(type: string): { type: 'icon'; src: string } | { type: 'emoji'; emoji: string } {
  const normalizedType = type.toLowerCase();
  const iconInfo = iconMap[normalizedType];
  
  if (iconInfo) {
    return { type: 'icon', src: iconInfo.src };
  }
  
  return { type: 'emoji', emoji: emojiMap[normalizedType] || '⚡' };
}

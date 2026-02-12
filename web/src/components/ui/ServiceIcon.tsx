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
  
  // Workflow node types - map to appropriate service icons
  start_email: { src: '/icons/gmail.svg' },
  send_email: { src: '/icons/gmail.svg' },
  append_row: { src: '/icons/sheets.svg' },
  read_sheet: { src: '/icons/sheets.svg' },
  send_slack: { src: '/icons/slack.svg' },
  ai_reply: { src: '/icons/openai.svg' },
  ai_summarize: { src: '/icons/openai.svg' },
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

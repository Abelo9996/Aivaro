'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

const colors = {
  primary: '#8b5cf6',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  darkBg: '#0a0a1a',
  darkerBg: '#050510',
};

export default function PrivacyPage() {
  return (
    <div style={{
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${colors.darkerBg} 0%, ${colors.darkBg} 50%, ${colors.darkerBg} 100%)`,
    }}>
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 24px 80px' }}>
        <Link href="/landing" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: colors.textMuted, textDecoration: 'none', fontSize: 14, marginBottom: 40 }}>
          <ArrowLeft size={18} /> Back to Home
        </Link>

        <h1 style={{ fontSize: 40, fontWeight: 800, color: colors.textPrimary, marginBottom: 8 }}>Privacy Policy</h1>
        <p style={{ fontSize: 14, color: colors.textMuted, marginBottom: 48 }}>Last updated: February 28, 2026</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 36 }}>
          <Section title="1. Introduction">
            Aivaro ("we", "our", "us") operates the Aivaro platform at aivaro-ai.com. This Privacy Policy explains how we collect, use, and protect your information when you use our service.
          </Section>

          <Section title="2. Information We Collect">
            <strong>Account Information:</strong> When you sign up, we collect your email address, name, and password (stored as a secure hash). We never store your password in plain text.
            <br /><br />
            <strong>Business Information:</strong> Information you provide about your business, including knowledge base entries, workflow configurations, and integration settings.
            <br /><br />
            <strong>Integration Data:</strong> When you connect third-party services (Google, Stripe, Slack, etc.), we store OAuth tokens and API keys to operate your workflows. We access only the data necessary to execute your configured workflows.
            <br /><br />
            <strong>Usage Data:</strong> We collect information about how you use the platform, including workflow execution logs, feature usage, and performance metrics.
          </Section>

          <Section title="3. How We Use Your Information">
            We use your information to:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Provide, operate, and maintain the Aivaro platform</li>
              <li>Execute your automated workflows on your behalf</li>
              <li>Send emails, SMS, and other communications as configured by you</li>
              <li>Process payments through your connected Stripe account</li>
              <li>Send you account-related communications (verification, password reset, security alerts)</li>
              <li>Improve and develop new features</li>
            </ul>
          </Section>

          <Section title="4. Third-Party Integrations">
            Aivaro connects to third-party services on your behalf. When you authorize an integration:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li><strong>Google:</strong> We access Gmail (send/read), Calendar (create events), and Sheets (read/write) using OAuth with the minimum required scopes</li>
              <li><strong>Stripe:</strong> We use your API key to create payment links, invoices, and check payment status</li>
              <li><strong>Twilio:</strong> We use your credentials to send SMS, WhatsApp messages, and make calls</li>
              <li><strong>Slack, Notion, Airtable, Calendly, Mailchimp:</strong> We access only the data needed to execute your workflows</li>
            </ul>
            <br />
            You can revoke any integration at any time from the Connections page. We do not sell or share your integration data with third parties.
          </Section>

          <Section title="5. Data Storage & Security">
            Your data is stored on secure servers hosted by Railway (backend) and Vercel (frontend). We use:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>HTTPS encryption for all data in transit</li>
              <li>Encrypted database connections</li>
              <li>Hashed passwords (bcrypt)</li>
              <li>OAuth tokens stored server-side only</li>
              <li>No client-side storage of sensitive credentials</li>
            </ul>
          </Section>

          <Section title="6. Data Retention">
            We retain your data for as long as your account is active. Workflow execution logs are retained for 90 days. If you delete your account, we will delete your personal data within 30 days, except where we are required by law to retain it.
          </Section>

          <Section title="7. Your Rights">
            You have the right to:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Access the personal data we hold about you</li>
              <li>Request correction of inaccurate data</li>
              <li>Request deletion of your account and data</li>
              <li>Export your data (workflow configurations, knowledge base entries)</li>
              <li>Revoke third-party integration access at any time</li>
            </ul>
          </Section>

          <Section title="8. Cookies">
            We use essential cookies only — specifically, an authentication token stored in your browser&apos;s local storage to keep you logged in. We do not use tracking cookies or third-party analytics cookies.
          </Section>

          <Section title="9. Children's Privacy">
            Aivaro is not intended for use by individuals under the age of 18. We do not knowingly collect personal information from children.
          </Section>

          <Section title="10. Changes to This Policy">
            We may update this Privacy Policy from time to time. We will notify you of material changes by email or through the platform.
          </Section>

          <Section title="11. Contact Us">
            If you have questions about this Privacy Policy, contact us at <a href="mailto:support@aivaro-ai.com" style={{ color: colors.primary, textDecoration: 'none' }}>support@aivaro-ai.com</a>.
          </Section>
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e2e8f0', marginBottom: 12 }}>{title}</h2>
      <div style={{ fontSize: 15, color: 'rgba(226, 232, 240, 0.75)', lineHeight: 1.7 }}>{children}</div>
    </div>
  );
}

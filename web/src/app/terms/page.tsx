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

export default function TermsPage() {
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

        <h1 style={{ fontSize: 40, fontWeight: 800, color: colors.textPrimary, marginBottom: 8 }}>Terms of Service</h1>
        <p style={{ fontSize: 14, color: colors.textMuted, marginBottom: 48 }}>Last updated: February 28, 2026</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 36 }}>
          <Section title="1. Acceptance of Terms">
            By accessing or using Aivaro ("the Service"), operated by Aivaro ("we", "our", "us"), you agree to be bound by these Terms of Service. If you do not agree, do not use the Service.
          </Section>

          <Section title="2. Description of Service">
            Aivaro is an AI-powered workflow automation platform for small and medium businesses. The Service allows you to:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Create automated workflows using natural language</li>
              <li>Connect third-party services (Google, Stripe, Twilio, Slack, etc.)</li>
              <li>Automate business operations including emails, payments, scheduling, and notifications</li>
              <li>Store business knowledge for AI-powered responses</li>
              <li>Use pre-built templates for common workflows</li>
            </ul>
          </Section>

          <Section title="3. Account Registration">
            You must provide a valid email address and verify it to create an account. You are responsible for:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Maintaining the confidentiality of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us immediately of any unauthorized use</li>
            </ul>
            You must be at least 18 years old to use the Service.
          </Section>

          <Section title="4. Free Trial & Plans">
            New accounts receive a 7-day free trial with limited features (1 workflow, 10 runs). No credit card is required for the trial. After the trial period, you must upgrade to a paid plan to continue using the Service. We reserve the right to modify plan features and pricing with reasonable notice.
          </Section>

          <Section title="5. Your Data & Content">
            You retain ownership of all data and content you provide to the Service, including:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Workflow configurations</li>
              <li>Knowledge base entries</li>
              <li>Business information</li>
              <li>Integration credentials</li>
            </ul>
            You grant us a limited license to use this data solely to provide and improve the Service.
          </Section>

          <Section title="6. Third-Party Integrations">
            The Service connects to third-party platforms. You are responsible for:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Complying with the terms of service of any third-party platform you connect</li>
              <li>Ensuring your workflows comply with the policies of connected services (e.g., email sending limits, Stripe acceptable use policy)</li>
              <li>The content of automated messages sent through your workflows</li>
            </ul>
            We are not responsible for the availability, accuracy, or actions of third-party services.
          </Section>

          <Section title="7. Acceptable Use">
            You agree not to use the Service to:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Send spam, unsolicited messages, or violate anti-spam laws (CAN-SPAM, GDPR, etc.)</li>
              <li>Engage in fraudulent, deceptive, or illegal activities</li>
              <li>Harass, abuse, or harm others</li>
              <li>Attempt to gain unauthorized access to the Service or other users&apos; accounts</li>
              <li>Interfere with or disrupt the Service&apos;s infrastructure</li>
              <li>Use automated workflows for any purpose that violates applicable law</li>
            </ul>
            We reserve the right to suspend or terminate accounts that violate these terms.
          </Section>

          <Section title="8. AI-Generated Content">
            The Service uses AI to generate workflow configurations, email content, and responses. You acknowledge that:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>AI-generated content may contain errors or inaccuracies</li>
              <li>You are responsible for reviewing and approving automated actions, especially those involving payments or external communications</li>
              <li>The approval workflow feature exists to give you control over sensitive actions — we recommend keeping it enabled</li>
            </ul>
          </Section>

          <Section title="9. Service Availability">
            We strive for high availability but do not guarantee uninterrupted service. We are not liable for:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Scheduled or unscheduled downtime</li>
              <li>Delays or failures in workflow execution</li>
              <li>Third-party service outages affecting your integrations</li>
            </ul>
          </Section>

          <Section title="10. Limitation of Liability">
            To the maximum extent permitted by law, Aivaro shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of profits, data, or business opportunities, arising from your use of the Service. Our total liability shall not exceed the amount you paid us in the 12 months preceding the claim.
          </Section>

          <Section title="11. Termination">
            You may delete your account at any time. We may terminate or suspend your account if you violate these Terms. Upon termination:
            <ul style={{ margin: '12px 0 0 20px', lineHeight: 2 }}>
              <li>Your workflows will stop executing</li>
              <li>Your data will be retained for 30 days, then deleted</li>
              <li>Connected third-party integrations will be revoked</li>
            </ul>
          </Section>

          <Section title="12. Changes to Terms">
            We may modify these Terms at any time. We will notify you of material changes via email or through the platform. Continued use of the Service after changes constitutes acceptance.
          </Section>

          <Section title="13. Governing Law">
            These Terms are governed by the laws of the State of California, United States, without regard to conflict of law principles.
          </Section>

          <Section title="14. Contact Us">
            Questions about these Terms? Contact us at <a href="mailto:support@aivaro-ai.com" style={{ color: colors.primary, textDecoration: 'none' }}>support@aivaro-ai.com</a>.
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

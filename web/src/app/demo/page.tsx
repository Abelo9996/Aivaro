'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, Play, MessageSquare, Zap, Shield, Bot, Clock, Mail } from 'lucide-react';

const styles = {
  primary: '#8b5cf6',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  accent: '#10b981',
};

export default function DemoPage() {
  return (
    <div style={{ 
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", 
      minHeight: '100vh',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Background */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, #0a0a1a 0%, #050510 100%)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(139, 92, 246, 0.08), transparent 60%)' }} />
      </div>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10, maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 48 }}
        >
          <Link href="/landing" style={{ textDecoration: 'none' }}>
            <motion.div
              style={{ display: 'flex', alignItems: 'center', gap: 6, color: styles.textMuted, fontSize: 14, fontWeight: 500, cursor: 'pointer' }}
              whileHover={{ color: styles.textPrimary }}
            >
              <ArrowLeft size={16} />
              Home
            </motion.div>
          </Link>
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <motion.div
              style={{ background: styles.primary, color: '#ffffff', padding: '8px 20px', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
              whileHover={{ opacity: 0.9 }}
              whileTap={{ scale: 0.97 }}
            >
              Get Started Free
              <ExternalLink size={14} />
            </motion.div>
          </Link>
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          style={{ textAlign: 'center', marginBottom: 40 }}
        >
          <h1 style={{ fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 700, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.1 }}>
            See Aivaro in action
          </h1>
          <p style={{ fontSize: 17, color: styles.textMuted, maxWidth: 480, margin: '0 auto', lineHeight: 1.6 }}>
            Describe what you need in plain English. Watch Aivaro build and run it.
          </p>
        </motion.div>

        {/* Video */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          style={{
            background: 'rgba(15, 15, 30, 0.8)',
            borderRadius: 14,
            border: '1px solid rgba(139, 92, 246, 0.2)',
            overflow: 'hidden',
            marginBottom: 48,
          }}
        >
          <div style={{ padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ display: 'flex', gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f56' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ffbd2e' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#27c93f' }} />
            </div>
            <span style={{ fontSize: 12, color: styles.textMuted, marginLeft: 8 }}>Aivaro Demo</span>
          </div>
          <video controls autoPlay muted playsInline style={{ width: '100%', display: 'block', background: '#000' }}>
            <source src="/Aivaro.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </motion.div>

        {/* Feature highlights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          style={{ marginBottom: 48 }}
        >
          <h2 style={{ fontSize: 22, fontWeight: 600, color: styles.textPrimary, textAlign: 'center', marginBottom: 28 }}>
            What you&apos;ll see
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
            {[
              { icon: <MessageSquare size={18} />, title: 'Natural Language Workflows', desc: 'Describe any workflow in plain English — Aivaro builds it with the right integrations.' },
              { icon: <Bot size={18} />, title: 'AI Knowledge Base', desc: 'Learns your pricing, policies, and voice. Every message sounds like you wrote it.' },
              { icon: <Shield size={18} />, title: 'Approval Gates', desc: 'Payments and external emails pause for your OK before going out.' },
              { icon: <Zap size={18} />, title: '8 Integrations', desc: 'Gmail, Stripe, Twilio, Slack, Airtable, Notion, Calendly, Mailchimp.' },
              { icon: <Clock size={18} />, title: 'Scheduled Triggers', desc: 'Run workflows on daily, weekly, or monthly schedules — automatically.' },
              { icon: <Mail size={18} />, title: 'Personalized Communication', desc: 'AI rewrites every email, SMS, and message to match your business voice.' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.5 + i * 0.06 }}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 12,
                  padding: 20,
                }}
              >
                <div style={{ color: styles.primary, marginBottom: 10 }}>{item.icon}</div>
                <h3 style={{ fontSize: 15, fontWeight: 600, color: styles.textPrimary, marginBottom: 4 }}>{item.title}</h3>
                <p style={{ fontSize: 13, color: styles.textMuted, margin: 0, lineHeight: 1.5 }}>{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          style={{
            background: 'rgba(139, 92, 246, 0.06)',
            borderRadius: 14,
            border: '1px solid rgba(139, 92, 246, 0.2)',
            padding: 36,
            textAlign: 'center',
            marginBottom: 48,
          }}
        >
          <h2 style={{ fontSize: 24, fontWeight: 700, color: styles.textPrimary, marginBottom: 10 }}>
            Ready to automate?
          </h2>
          <p style={{ fontSize: 15, color: styles.textMuted, marginBottom: 24 }}>
            7-day free trial. No credit card required.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{ background: styles.primary, color: '#fff', padding: '12px 24px', borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: 'pointer' }}
                whileHover={{ opacity: 0.9 }}
                whileTap={{ scale: 0.97 }}
              >
                Start Free Trial
              </motion.div>
            </Link>
            <Link href="/landing" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{ color: styles.textSecondary, padding: '12px 24px', borderRadius: 8, fontSize: 15, fontWeight: 500, border: '1px solid rgba(255,255,255,0.12)', cursor: 'pointer' }}
                whileHover={{ borderColor: 'rgba(255,255,255,0.25)' }}
              >
                Learn More
              </motion.div>
            </Link>
          </div>
        </motion.div>

        {/* Footer */}
        <div style={{ paddingTop: 24, borderTop: '1px solid rgba(255,255,255,0.06)', textAlign: 'center' }}>
          <p style={{ fontSize: 13, color: styles.textMuted }}>© 2026 Aivaro</p>
        </div>
      </div>
    </div>
  );
}

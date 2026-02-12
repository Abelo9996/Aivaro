'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, Play } from 'lucide-react';

const styles = {
  primary: '#8b5cf6',
  textPrimary: '#ffffff',
  textSecondary: 'rgba(214, 221, 230, 0.8)',
  textMuted: 'rgba(214, 221, 230, 0.5)',
  darkBg: '#0a0a1a',
};

export default function DemoPage() {
  return (
    <div style={{ 
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", 
      minHeight: '100vh',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Fixed Background */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom right, #0a0a1a 0%, #050510 50%, #020306 100%)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(139, 92, 246, 0.15), transparent 50%)' }} />
        <div style={{ position: 'absolute', top: '-10%', left: '20%', width: '800px', height: '800px', background: 'radial-gradient(circle, #8b5cf6 0%, transparent 70%)', filter: 'blur(120px)', opacity: 0.2 }} />
      </div>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10, maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: 48
          }}
        >
          <Link href="/landing" style={{ textDecoration: 'none' }}>
            <motion.div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                color: styles.textSecondary,
                fontSize: 14,
                fontWeight: 500,
                cursor: 'pointer'
              }}
              whileHover={{ color: styles.primary }}
            >
              <ArrowLeft size={18} />
              Back to Home
            </motion.div>
          </Link>
          
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <motion.div
              style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                color: '#ffffff',
                padding: '10px 20px',
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started
              <ExternalLink size={16} />
            </motion.div>
          </Link>
        </motion.div>

        {/* Title Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          style={{ textAlign: 'center', marginBottom: 48 }}
        >
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 16px',
            borderRadius: 999,
            border: '1px solid rgba(139, 92, 246, 0.4)',
            background: 'rgba(139, 92, 246, 0.1)',
            marginBottom: 24
          }}>
            <Play size={14} color={styles.primary} />
            <span style={{ fontSize: 14, color: styles.primary, fontWeight: 600 }}>Product Demo</span>
          </div>
          
          <h1 style={{
            fontSize: 'clamp(32px, 5vw, 56px)',
            fontWeight: 800,
            color: styles.textPrimary,
            marginBottom: 16,
            lineHeight: 1.1
          }}>
            See Aivaro in Action
          </h1>
          
          <p style={{
            fontSize: 'clamp(16px, 2vw, 20px)',
            color: styles.textSecondary,
            maxWidth: 600,
            margin: '0 auto',
            lineHeight: 1.6
          }}>
            Watch how Aivaro transforms plain English into powerful automated workflows. 
            No coding required — just describe what you need.
          </p>
        </motion.div>

        {/* Video Container */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          style={{
            background: 'linear-gradient(135deg, rgba(30, 30, 40, 0.95) 0%, rgba(20, 20, 35, 0.95) 100%)',
            borderRadius: 20,
            border: '2px solid rgba(139, 92, 246, 0.3)',
            overflow: 'hidden',
            boxShadow: '0 30px 80px rgba(0, 0, 0, 0.5), 0 0 60px rgba(139, 92, 246, 0.2)',
            marginBottom: 48
          }}
        >
          {/* Browser Chrome */}
          <div style={{ 
            background: 'rgba(40, 40, 55, 0.8)',
            padding: '12px 20px',
            borderBottom: '1px solid rgba(139, 92, 246, 0.2)',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f56' }} />
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ffbd2e' }} />
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#27c93f' }} />
            </div>
            <div style={{ 
              flex: 1,
              background: 'rgba(10, 10, 26, 0.6)',
              borderRadius: 8,
              padding: '6px 16px',
              fontSize: 13,
              color: styles.textMuted,
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <span>🎬 Aivaro Demo Video</span>
            </div>
          </div>
          
          {/* Video */}
          <video
            controls
            autoPlay
            muted
            playsInline
            style={{
              width: '100%',
              display: 'block',
              background: '#000'
            }}
          >
            <source src="/Aivaro.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </motion.div>

        {/* Key Features Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          style={{ marginBottom: 64 }}
        >
          <h2 style={{
            fontSize: 24,
            fontWeight: 700,
            color: styles.textPrimary,
            textAlign: 'center',
            marginBottom: 32
          }}>
            What You&apos;ll See in This Demo
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: 20
          }}>
            {[
              { title: 'AI Workflow Generation', desc: 'Describe your workflow in plain English and watch AI build it instantly' },
              { title: 'Email-Triggered Automation', desc: 'See how workflows trigger automatically when matching emails arrive' },
              { title: 'Google & Stripe Integration', desc: 'One-click OAuth connections to Gmail, Sheets, Calendar, and Stripe' },
              { title: 'Human Approval Guardrails', desc: 'Sensitive actions pause for your approval before executing' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + i * 0.1 }}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: 12,
                  padding: 24
                }}
              >
                <h3 style={{ fontSize: 16, fontWeight: 600, color: styles.textPrimary, marginBottom: 8 }}>
                  {item.title}
                </h3>
                <p style={{ fontSize: 14, color: styles.textSecondary, margin: 0, lineHeight: 1.5 }}>
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.1))',
            borderRadius: 16,
            border: '1.5px solid rgba(139, 92, 246, 0.4)',
            padding: 40,
            textAlign: 'center'
          }}
        >
          <h2 style={{ fontSize: 28, fontWeight: 700, color: styles.textPrimary, marginBottom: 12 }}>
            Ready to Automate Your Business?
          </h2>
          <p style={{ fontSize: 16, color: styles.textSecondary, marginBottom: 24 }}>
            Start building your first workflow in minutes. No credit card required.
          </p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: '#ffffff',
                  padding: '14px 28px',
                  borderRadius: 8,
                  fontSize: 16,
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Get Started Free
              </motion.div>
            </Link>
            <Link href="/landing" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{
                  background: 'transparent',
                  color: styles.primary,
                  padding: '14px 28px',
                  borderRadius: 8,
                  fontSize: 16,
                  fontWeight: 600,
                  border: `2px solid ${styles.primary}`,
                  cursor: 'pointer'
                }}
                whileHover={{ scale: 1.05, background: 'rgba(139, 92, 246, 0.1)' }}
                whileTap={{ scale: 0.95 }}
              >
                Learn More
              </motion.div>
            </Link>
          </div>
        </motion.div>

        {/* Footer */}
        <div style={{
          marginTop: 64,
          paddingTop: 32,
          borderTop: '1px solid rgba(139, 92, 246, 0.2)',
          textAlign: 'center'
        }}>
          <p style={{ fontSize: 14, color: styles.textMuted }}>
            © 2026 Aivaro. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}

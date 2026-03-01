'use client';

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { ArrowRight, Zap, Shield, Clock, Check, Bot, Mail, DollarSign, Calendar, Bell, Menu, X, MessageSquare, ChevronDown } from 'lucide-react';

const styles = {
  primary: '#8b5cf6',
  primaryLight: '#a78bfa',
  accent: '#10b981',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
};

function useResponsive() {
  const [windowSize, setWindowSize] = useState({ width: 1200, height: 800 });
  useEffect(() => {
    function handleResize() {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    }
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  return {
    isMobile: windowSize.width < 768,
    isTablet: windowSize.width >= 768 && windowSize.width < 1024,
    isDesktop: windowSize.width >= 1024,
    width: windowSize.width,
  };
}

const smoothScrollTo = (elementId: string) => {
  const element = document.getElementById(elementId);
  if (element) element.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

function Logo({ small = false }: { small?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <img src="/logo.png" alt="Aivaro" style={{ height: small ? 32 : 40, width: 'auto' }} />
    </div>
  );
}

function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isMobile, isTablet } = useResponsive();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <motion.div
        style={{
          backgroundColor: scrolled || mobileMenuOpen ? 'rgba(10, 10, 26, 0.95)' : 'transparent',
          backdropFilter: scrolled || mobileMenuOpen ? 'blur(20px)' : 'none',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          borderBottom: scrolled ? '1px solid rgba(139, 92, 246, 0.2)' : 'none',
          transition: 'all 500ms',
          width: '100%'
        }}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '8px 16px' : isTablet ? '8px 32px' : '8px 64px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 0',
          }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Logo small={isMobile} />
            </Link>

            {!isMobile && !isTablet && (
              <div style={{ display: 'flex', gap: 32, alignItems: 'center' }}>
                {['how-it-works', 'results', 'pricing'].map((item) => (
                  <motion.a
                    key={item}
                    href={`#${item}`}
                    onClick={(e) => { e.preventDefault(); smoothScrollTo(item); }}
                    style={{ color: styles.textMuted, fontSize: 14, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', textTransform: 'capitalize' }}
                    whileHover={{ color: styles.textPrimary }}
                  >
                    {item.replace(/-/g, ' ')}
                  </motion.a>
                ))}
              </div>
            )}

            {!isMobile && (
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <Link href="/login" style={{ textDecoration: 'none' }}>
                  <motion.div
                    style={{ color: styles.textSecondary, padding: '8px 16px', fontSize: 14, fontWeight: 500, cursor: 'pointer' }}
                    whileHover={{ color: styles.textPrimary }}
                  >
                    Sign in
                  </motion.div>
                </Link>
                <Link href="/signup" style={{ textDecoration: 'none' }}>
                  <motion.div
                    style={{ background: styles.primary, color: '#ffffff', padding: '8px 20px', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
                    whileHover={{ opacity: 0.9 }}
                    whileTap={{ scale: 0.97 }}
                  >
                    Get Started Free
                  </motion.div>
                </Link>
              </div>
            )}

            {(isMobile || isTablet) && (
              <motion.button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                style={{ background: 'transparent', border: 'none', color: styles.textPrimary, cursor: 'pointer', padding: 8 }}
                whileTap={{ scale: 0.95 }}
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>

      {(isMobile || isTablet) && mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ position: 'fixed', top: 60, left: 0, right: 0, background: 'rgba(10, 10, 26, 0.98)', backdropFilter: 'blur(20px)', zIndex: 999, padding: '24px 16px', borderBottom: '1px solid rgba(139, 92, 246, 0.2)' }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {['how-it-works', 'results', 'pricing'].map((item) => (
              <motion.a
                key={item}
                href={`#${item}`}
                onClick={(e) => { e.preventDefault(); smoothScrollTo(item); setMobileMenuOpen(false); }}
                style={{ color: styles.textPrimary, fontSize: 18, fontWeight: 500, textDecoration: 'none', padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.1)', textTransform: 'capitalize' }}
              >
                {item.replace(/-/g, ' ')}
              </motion.a>
            ))}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 16 }}>
              <Link href="/login" style={{ textDecoration: 'none' }}>
                <div style={{ color: styles.textPrimary, padding: '14px 24px', borderRadius: 8, fontSize: 16, border: '1px solid rgba(255,255,255,0.15)', textAlign: 'center' }}>Sign in</div>
              </Link>
              <Link href="/signup" style={{ textDecoration: 'none' }}>
                <div style={{ background: styles.primary, color: '#ffffff', padding: '14px 24px', borderRadius: 8, fontSize: 16, fontWeight: 600, textAlign: 'center' }}>Get Started Free</div>
              </Link>
            </div>
          </div>
        </motion.div>
      )}
    </>
  );
}

function HeroSection() {
  const { isMobile, isTablet } = useResponsive();

  return (
    <div style={{ background: 'transparent', position: 'relative' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '64px 16px 48px' : isTablet ? '80px 32px 64px' : '120px 64px 80px' }}>
        <motion.div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>

          <motion.div
            style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 999, border: '1px solid rgba(16, 185, 129, 0.35)', background: 'rgba(16, 185, 129, 0.08)', marginBottom: isMobile ? 24 : 32 }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', display: 'inline-block', animation: 'pulse 2s ease-in-out infinite' }} />
            <span style={{ fontSize: 13, color: '#6ee7b7', fontWeight: 500 }}>Trusted by 15+ businesses in beta</span>
          </motion.div>

          <motion.h1
            style={{ fontSize: isMobile ? 36 : isTablet ? 52 : 64, lineHeight: 1.05, letterSpacing: '-1.5px', fontWeight: 700, color: styles.textPrimary, margin: '0 0 20px', maxWidth: 800 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            Automate your business{' '}
            <span style={{
              background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 40%, #10b981 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              in plain English
            </span>
          </motion.h1>

          <motion.p
            style={{ fontSize: isMobile ? 17 : 19, lineHeight: 1.6, color: styles.textMuted, margin: '0 0 36px', maxWidth: 580 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Describe what you need. Aivaro builds the workflow, connects your tools, and runs it 24/7.
          </motion.p>

          <motion.div
            style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 12, alignItems: 'center', width: isMobile ? '100%' : 'auto', marginBottom: 12 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Link href="/signup" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{ background: styles.primary, color: '#ffffff', padding: '14px 32px', borderRadius: 10, fontSize: 16, fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8, width: isMobile ? '100%' : 'auto' }}
                whileHover={{ opacity: 0.9 }}
                whileTap={{ scale: 0.97 }}
              >
                Start Free Trial
                <ArrowRight size={18} />
              </motion.div>
            </Link>
            <Link href="/demo" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{ color: styles.textSecondary, padding: '14px 32px', borderRadius: 10, fontSize: 16, fontWeight: 500, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8, border: '1px solid rgba(255,255,255,0.12)', width: isMobile ? '100%' : 'auto' }}
                whileHover={{ borderColor: 'rgba(255,255,255,0.25)' }}
              >
                See How It Works
              </motion.div>
            </Link>
          </motion.div>

          <motion.p
            style={{ fontSize: 13, color: styles.textMuted, margin: 0 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            No credit card required &middot; 7-day free trial
          </motion.p>

          {/* Chat example card */}
          <motion.div
            style={{ width: '100%', maxWidth: 720, marginTop: isMobile ? 40 : 56 }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5 }}
          >
            <div style={{
              background: 'rgba(15, 15, 30, 0.8)',
              borderRadius: 14,
              border: '1px solid rgba(139, 92, 246, 0.2)',
              overflow: 'hidden',
            }}>
              <div style={{ padding: '12px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <MessageSquare size={14} color={styles.primary} />
                <span style={{ fontSize: 12, color: styles.textMuted, fontWeight: 500 }}>Aivaro Chat</span>
              </div>
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {/* User message */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <div style={{ background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.2)', borderRadius: '14px 14px 4px 14px', padding: '12px 16px', maxWidth: '80%' }}>
                      <p style={{ fontSize: 14, color: styles.textPrimary, margin: 0, lineHeight: 1.5 }}>
                        &ldquo;When someone books, collect a $50 deposit and send them a reminder the day before&rdquo;
                      </p>
                    </div>
                  </div>
                  {/* AI response */}
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '14px 14px 14px 4px', padding: '12px 16px', maxWidth: '85%' }}>
                      <p style={{ fontSize: 14, color: styles.textSecondary, margin: '0 0 10px', lineHeight: 1.5 }}>
                        Done! I created a 3-step workflow:
                      </p>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {['Stripe $50 deposit', 'Confirmation email', 'SMS reminder'].map((step, i) => (
                          <span key={i} style={{ fontSize: 12, padding: '4px 10px', borderRadius: 6, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', color: styles.accent, fontWeight: 500 }}>
                            {step}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            style={{ marginTop: isMobile ? 32 : 48 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4, y: [0, 6, 0] }}
            transition={{ duration: 2, repeat: Infinity, delay: 1 }}
          >
            <ChevronDown size={20} color={styles.textMuted} />
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}

function HowItWorksSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const steps = [
    { number: '1', title: 'Connect your tools', description: 'Gmail, Calendar, Stripe, Slack, Twilio, Airtable, Notion, Calendly, Mailchimp — one-click setup.', icon: <Zap size={20} /> },
    { number: '2', title: 'Describe what you need', description: 'Tell Aivaro in plain English or pick a template. It asks the right questions, then builds it.', icon: <MessageSquare size={20} /> },
    { number: '3', title: 'It runs 24/7', description: 'Workflows trigger on emails, schedules, or webhooks. Every message matches your voice.', icon: <Bot size={20} /> },
  ];

  return (
    <div id="how-it-works" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 56 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            Running in minutes, <span style={{ background: 'linear-gradient(135deg, #a78bfa, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>not days</span>
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted }}>
            No developers. No drag-and-drop. No setup guide.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', gap: isMobile ? 16 : 20 }}>
          {steps.map((step, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 24 : 28,
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'rgba(139, 92, 246, 0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 16, color: styles.primary,
              }}>
                <span style={{ fontSize: 18, fontWeight: 700 }}>{step.number}</span>
              </div>
              <h3 style={{ fontSize: isMobile ? 18 : 20, fontWeight: 600, marginBottom: 8, color: styles.textPrimary }}>{step.title}</h3>
              <p style={{ fontSize: 15, color: styles.textMuted, margin: 0, lineHeight: 1.6 }}>{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ResultsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const metrics = [
    { value: '8%', label: 'No-show rate', detail: 'Down from 25%' },
    { value: '5h+', label: 'Saved per week', detail: 'Per business' },
    { value: '15', label: 'Pilot users', detail: 'Pre-revenue beta' },
    { value: '24/7', label: 'Always running', detail: 'Zero manual work' },
  ];

  return (
    <div id="results" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 56 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            Real results from <span style={{ background: 'linear-gradient(135deg, #10b981, #6ee7b7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>real businesses</span>
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted, maxWidth: 500, margin: '0 auto' }}>
            Our first pilot — a liquidation business — went from manual chaos to automated operations.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', gap: isMobile ? 12 : 16, marginBottom: isMobile ? 40 : 56 }}>
          {metrics.map((stat, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 20 : 24,
                textAlign: 'center',
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.2 + i * 0.08 }}
            >
              <div style={{ fontSize: isMobile ? 28 : 36, fontWeight: 700, color: styles.primary, marginBottom: 4 }}>{stat.value}</div>
              <div style={{ fontSize: 14, color: styles.textPrimary, fontWeight: 600, marginBottom: 2 }}>{stat.label}</div>
              <div style={{ fontSize: 12, color: styles.textMuted }}>{stat.detail}</div>
            </motion.div>
          ))}
        </div>

        {/* Before / After */}
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)', gap: 16 }}>
          <motion.div
            style={{
              background: 'rgba(239, 68, 68, 0.04)',
              borderRadius: 14,
              border: '1px solid rgba(239, 68, 68, 0.15)',
              padding: isMobile ? 20 : 28,
            }}
            initial={{ opacity: 0, x: -20 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <h3 style={{ fontSize: 13, fontWeight: 600, color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Before</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                '6-8 hours/week on manual booking confirmations',
                '20-25% no-show rate',
                'Missed follow-ups and cold leads',
                'Needed technical help for basic automation',
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <X size={14} style={{ color: '#ef4444', flexShrink: 0 }} />
                  <span style={{ fontSize: 14, color: styles.textSecondary, lineHeight: 1.5 }}>{item}</span>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            style={{
              background: 'rgba(16, 185, 129, 0.04)',
              borderRadius: 14,
              border: '1px solid rgba(16, 185, 129, 0.15)',
              padding: isMobile ? 20 : 28,
            }}
            initial={{ opacity: 0, x: 20 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <h3 style={{ fontSize: 13, fontWeight: 600, color: styles.accent, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>After Aivaro</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                'Bookings confirmed automatically in seconds',
                'No-show rate dropped to 8%',
                '~5 hours/week saved on operations',
                'Zero technical knowledge needed',
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Check size={14} style={{ color: styles.accent, flexShrink: 0 }} />
                  <span style={{ fontSize: 14, color: styles.textSecondary, lineHeight: 1.5 }}>{item}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function FeaturesSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const features = [
    { icon: <MessageSquare size={20} />, title: 'Natural Language Workflows', description: 'Describe what you need in plain English. Aivaro builds it — no drag-and-drop required.' },
    { icon: <Bot size={20} />, title: 'AI Knowledge Base', description: 'Stores your pricing, policies, and tone. Every message sounds like you wrote it.' },
    { icon: <Shield size={20} />, title: 'Approval Gates', description: 'Sensitive actions (payments, external emails) require your OK before sending.' },
    { icon: <Mail size={20} />, title: 'Personalized Communication', description: 'AI rewrites every email, SMS, and message to match your voice.' },
    { icon: <Zap size={20} />, title: '8 Integrations', description: 'Gmail, Stripe, Twilio, Slack, Airtable, Notion, Calendly, Mailchimp — all connected.' },
    { icon: <Clock size={20} />, title: 'Scheduled Triggers', description: 'Run workflows on a schedule — daily reports, weekly invoices, monthly summaries.' },
  ];

  return (
    <div style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 56 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            Everything you need to automate
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted }}>
            Built for founders and operators, not engineers.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)', gap: isMobile ? 12 : 16 }}>
          {features.map((f, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 20 : 24,
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: i * 0.06 }}
            >
              <div style={{ color: styles.primary, marginBottom: 12 }}>{f.icon}</div>
              <h3 style={{ fontSize: 16, fontWeight: 600, color: styles.textPrimary, marginBottom: 6 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: styles.textMuted, margin: 0, lineHeight: 1.6 }}>{f.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PricingSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const plans = [
    {
      name: 'Free Trial',
      price: '$0',
      period: '7 days',
      features: ['1 workflow', '10 runs', 'Core integrations', 'Template library', 'Knowledge base'],
      cta: 'Start Free',
      popular: false,
      href: '/signup',
    },
    {
      name: 'Starter',
      price: '$29',
      period: '/month',
      features: ['5 workflows', '100 runs/month', 'All integrations', 'AI agent tasks', 'Email & schedule triggers'],
      cta: 'Get Started',
      popular: false,
      href: '/signup',
    },
    {
      name: 'Growth',
      price: '$79',
      period: '/month',
      features: ['Unlimited workflows', '500 runs/month', 'All integrations', 'AI agent tasks', 'File import', 'Priority support'],
      cta: 'Get Started',
      popular: true,
      href: '/signup',
    },
    {
      name: 'Business',
      price: '$199',
      period: '/month',
      features: ['Unlimited everything', 'Dedicated onboarding', 'Custom integrations', 'Advanced analytics', 'Team access'],
      cta: 'Contact Us',
      popular: false,
      href: '/signup',
    },
  ];

  return (
    <div id="pricing" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 56 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            Simple, transparent pricing
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted }}>
            Start free. Upgrade when you&apos;re ready.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', gap: isMobile ? 16 : 16 }}>
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              style={{
                background: plan.popular ? 'rgba(139, 92, 246, 0.06)' : 'rgba(255, 255, 255, 0.03)',
                borderRadius: 14,
                border: plan.popular ? '1.5px solid rgba(139, 92, 246, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 24 : 28,
                position: 'relative',
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              {plan.popular && (
                <div style={{ position: 'absolute', top: -10, left: '50%', transform: 'translateX(-50%)', background: styles.primary, color: '#fff', padding: '3px 12px', borderRadius: 999, fontSize: 11, fontWeight: 600 }}>
                  Popular
                </div>
              )}
              <h3 style={{ fontSize: 18, fontWeight: 600, color: styles.textPrimary, marginBottom: 4 }}>{plan.name}</h3>
              <div style={{ marginBottom: 20 }}>
                <span style={{ fontSize: 32, fontWeight: 700, color: styles.textPrimary }}>{plan.price}</span>
                <span style={{ fontSize: 14, color: styles.textMuted }}>{plan.period}</span>
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 24px' }}>
                {plan.features.map((f, j) => (
                  <li key={j} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <Check size={14} style={{ color: styles.accent, flexShrink: 0 }} />
                    <span style={{ fontSize: 13, color: styles.textSecondary }}>{f}</span>
                  </li>
                ))}
              </ul>
              <Link href={plan.href} style={{ textDecoration: 'none' }}>
                <motion.div
                  style={{
                    width: '100%',
                    background: plan.popular ? styles.primary : 'transparent',
                    color: plan.popular ? '#fff' : styles.textSecondary,
                    padding: '10px 20px',
                    borderRadius: 8,
                    fontSize: 14,
                    fontWeight: 600,
                    border: plan.popular ? 'none' : '1px solid rgba(255,255,255,0.15)',
                    cursor: 'pointer',
                    textAlign: 'center',
                  }}
                  whileHover={{ opacity: 0.9 }}
                  whileTap={{ scale: 0.97 }}
                >
                  {plan.cta}
                </motion.div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CTASection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  return (
    <div style={{ padding: isMobile ? '48px 0' : '80px 0' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          ref={ref}
          style={{
            background: 'rgba(139, 92, 246, 0.06)',
            borderRadius: 16,
            border: '1px solid rgba(139, 92, 246, 0.2)',
            padding: isMobile ? 32 : 48,
            textAlign: 'center',
          }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
        >
          <h2 style={{ fontSize: isMobile ? 24 : 36, fontWeight: 700, color: styles.textPrimary, marginBottom: 12 }}>
            Your next missed follow-up costs more than trying Aivaro
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted, marginBottom: 28, maxWidth: 520, margin: '0 auto 28px' }}>
            7-day free trial. First workflow running in minutes.
          </p>
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <motion.div
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: styles.primary, color: '#fff',
                padding: isMobile ? '14px 28px' : '16px 32px',
                borderRadius: 10, fontSize: 16, fontWeight: 600, cursor: 'pointer',
              }}
              whileHover={{ opacity: 0.9 }}
              whileTap={{ scale: 0.97 }}
            >
              Start Automating Free
              <ArrowRight size={18} />
            </motion.div>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}

function Footer() {
  const { isMobile, isTablet } = useResponsive();
  return (
    <div style={{ padding: isMobile ? '32px 0' : '48px 0', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', justifyContent: 'space-between', gap: 16 }}>
          <div>
            <Logo small />
            <p style={{ fontSize: 13, color: styles.textMuted, marginTop: 6 }}>Automate your business in plain English.</p>
          </div>
          <div style={{ display: 'flex', gap: 24 }}>
            {[
              { label: 'Privacy', href: '/privacy' },
              { label: 'Terms', href: '/terms' },
              { label: 'Demo', href: '/demo' },
            ].map((item) => (
              <Link key={item.label} href={item.href} style={{ fontSize: 13, color: styles.textMuted, textDecoration: 'none' }}>
                {item.label}
              </Link>
            ))}
          </div>
          <p style={{ fontSize: 13, color: styles.textMuted }}>© 2026 Aivaro</p>
        </div>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div style={{
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      minHeight: '100vh',
      position: 'relative',
      overflowX: 'hidden',
    }}>
      {/* Keyframe animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.85); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          50% { transform: translateY(-30px) translateX(10px); }
        }
      `}</style>
      {/* Background */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, #0a0a1a 0%, #050510 100%)' }} />
        {/* Dot grid pattern */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'radial-gradient(rgba(139, 92, 246, 0.15) 1px, transparent 1px)',
          backgroundSize: '32px 32px',
          maskImage: 'radial-gradient(ellipse at 50% 0%, black 0%, transparent 70%)',
          WebkitMaskImage: 'radial-gradient(ellipse at 50% 0%, black 0%, transparent 70%)',
        }} />
        {/* Primary glow */}
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% -10%, rgba(139, 92, 246, 0.15), transparent 55%)' }} />
        {/* Secondary accent glow */}
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.06), transparent 50%)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 80% 50%, rgba(16, 185, 129, 0.04), transparent 50%)' }} />
        {/* Floating orbs */}
        <div style={{ position: 'absolute', top: '15%', left: '10%', width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(139, 92, 246, 0.06), transparent 70%)', animation: 'float 8s ease-in-out infinite', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', top: '60%', right: '8%', width: 200, height: 200, borderRadius: '50%', background: 'radial-gradient(circle, rgba(16, 185, 129, 0.05), transparent 70%)', animation: 'float-slow 12s ease-in-out infinite', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', top: '40%', left: '60%', width: 150, height: 150, borderRadius: '50%', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.05), transparent 70%)', animation: 'float 10s ease-in-out infinite 2s', pointerEvents: 'none' }} />
      </div>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        <Header />
        <HeroSection />
        <HowItWorksSection />
        <ResultsSection />
        <FeaturesSection />
        <PricingSection />
        <CTASection />
        <Footer />
      </div>
    </div>
  );
}

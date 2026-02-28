'use client';

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Zap, Shield, TrendingUp, Clock, Check, Bot, Mail, DollarSign, Calendar, BarChart3, Bell, Menu, X, Play, MessageSquare, ChevronRight } from 'lucide-react';

const styles = {
  primary: '#8b5cf6',
  primaryLight: '#a78bfa',
  secondary: '#3b82f6',
  accent: '#10b981',
  cyan: '#06b6d4',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  darkBg: '#0a0a1a',
  darkerBg: '#050510',
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
            padding: isMobile ? '8px 0' : '8px 24px',
          }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Logo small={isMobile} />
            </Link>

            {!isMobile && !isTablet && (
              <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
                {['how-it-works', 'results', 'pricing'].map((item) => (
                  <motion.a
                    key={item}
                    href={`#${item}`}
                    onClick={(e) => { e.preventDefault(); smoothScrollTo(item); }}
                    style={{ color: styles.textSecondary, fontSize: 15, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', textTransform: 'capitalize' }}
                    whileHover={{ color: styles.primary }}
                  >
                    {item.replace(/-/g, ' ')}
                  </motion.a>
                ))}
              </div>
            )}

            {!isMobile && (
              <div style={{ display: 'flex', gap: 12 }}>
                <Link href="/login" style={{ textDecoration: 'none' }}>
                  <motion.div
                    style={{ background: 'transparent', color: styles.textPrimary, padding: '8px 16px', borderRadius: 999, fontSize: 15, border: '1.5px solid rgba(139, 92, 246, 0.3)', cursor: 'pointer' }}
                    whileHover={{ borderColor: 'rgba(139, 92, 246, 0.6)', background: 'rgba(139, 92, 246, 0.1)' }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Sign in
                  </motion.div>
                </Link>
                <Link href="/signup" style={{ textDecoration: 'none' }}>
                  <motion.div
                    style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', color: '#ffffff', padding: '8px 16px', borderRadius: 999, fontSize: 15, fontWeight: 600, cursor: 'pointer' }}
                    whileHover={{ scale: 1.05, boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)' }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Start Free Trial — No Card Required
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
                <div style={{ background: 'transparent', color: styles.textPrimary, padding: '14px 24px', borderRadius: 8, fontSize: 16, border: '1.5px solid rgba(139, 92, 246, 0.3)', textAlign: 'center' }}>Sign in</div>
              </Link>
              <Link href="/signup" style={{ textDecoration: 'none' }}>
                <div style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', color: '#ffffff', padding: '14px 24px', borderRadius: 8, fontSize: 16, fontWeight: 600, textAlign: 'center' }}>Start Free Trial</div>
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
    <div style={{ background: 'transparent', position: 'relative', overflow: 'hidden' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '48px 16px' : isTablet ? '64px 32px' : '96px 64px' }}>
        <motion.div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 24 : 40, alignItems: 'center' }}>

          <motion.div
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 999, border: '1px solid rgba(16, 185, 129, 0.4)', background: 'rgba(16, 185, 129, 0.1)' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span style={{ fontSize: isMobile ? 12 : 14, color: styles.accent, fontWeight: 600 }}>✅ Already saving one business 5+ hours/week</span>
          </motion.div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 16 : 24, alignItems: 'center', maxWidth: 1000 }}>
            <motion.h1
              style={{ fontSize: isMobile ? 36 : isTablet ? 48 : 68, lineHeight: 1.08, letterSpacing: '-2px', fontWeight: 800, color: styles.textPrimary, textAlign: 'center', margin: 0 }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Stop Losing Money on{' '}
              <span style={{ background: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Missed Follow-Ups
              </span>
            </motion.h1>
            <motion.p
              style={{ fontSize: isMobile ? 17 : isTablet ? 20 : 22, lineHeight: '1.6', color: styles.textSecondary, textAlign: 'center', margin: 0, maxWidth: 680 }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              Aivaro automates your bookings, deposits, reminders, and client communication. Tell it what you need in plain English, pick a template, or let it handle tasks like an AI assistant. It learns your business and runs 24/7.
            </motion.p>
          </div>

          <motion.div
            style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 16, alignItems: 'center', width: isMobile ? '100%' : 'auto' }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Link href="/signup" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', color: '#ffffff', padding: isMobile ? '16px 24px' : '18px 36px', borderRadius: 10, fontSize: isMobile ? 16 : 18, fontWeight: 700, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8, boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)', width: isMobile ? '100%' : 'auto' }}
                whileHover={{ scale: 1.05, boxShadow: '0 6px 30px rgba(139, 92, 246, 0.6)' }}
                whileTap={{ scale: 0.95 }}
              >
                Automate My Business Free
                <ArrowRight size={20} />
              </motion.div>
            </Link>
          </motion.div>

          <motion.p
            style={{ fontSize: 14, color: styles.textMuted, textAlign: 'center', margin: 0 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            No credit card required • First workflow running in 10 minutes
          </motion.p>

          {/* Concrete example */}
          <motion.div
            style={{ width: '100%', maxWidth: 900, marginTop: isMobile ? 24 : 48 }}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <div style={{
              background: 'rgba(20, 20, 35, 0.9)',
              borderRadius: 16,
              border: '1.5px solid rgba(139, 92, 246, 0.3)',
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
            }}>
              <div style={{ padding: isMobile ? '12px 16px' : '16px 24px', borderBottom: '1px solid rgba(139, 92, 246, 0.15)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <MessageSquare size={16} color={styles.primary} />
                <span style={{ fontSize: 13, color: styles.textMuted }}>You tell Aivaro:</span>
              </div>
              <div style={{ padding: isMobile ? '20px 16px' : '28px 24px' }}>
                <p style={{ fontSize: isMobile ? 16 : 20, color: styles.textPrimary, margin: 0, lineHeight: 1.6, fontStyle: 'italic' }}>
                  "When someone books a pickup, collect a $50 deposit via Stripe, send them a confirmation with our cancellation policy, and text me a reminder the day before."
                </p>
              </div>
              <div style={{ padding: isMobile ? '16px' : '20px 24px', background: 'rgba(139, 92, 246, 0.06)', borderTop: '1px solid rgba(139, 92, 246, 0.15)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <Zap size={14} color={styles.accent} />
                  <span style={{ fontSize: 13, color: styles.accent, fontWeight: 600 }}>Aivaro generates & runs:</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {['Booking form', 'Stripe $50 deposit', 'Confirmation email', 'Calendar event', 'SMS reminder', 'No-show tracking'].map((step, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', gap: 6,
                      padding: '6px 12px', borderRadius: 8,
                      background: 'rgba(139, 92, 246, 0.12)',
                      border: '1px solid rgba(139, 92, 246, 0.25)',
                      fontSize: 13, color: styles.textPrimary, fontWeight: 500,
                    }}>
                      <Check size={12} color={styles.accent} />
                      {step}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

        </motion.div>
      </div>
    </div>
  );
}

function PainSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const { isMobile, isTablet } = useResponsive();

  const pains = [
    { icon: <Clock size={24} />, title: 'Leads go cold', description: 'You get a booking request at 9 PM. You respond at 10 AM. They already went with someone else.', color: '#ef4444' },
    { icon: <DollarSign size={24} />, title: 'No-shows eat your revenue', description: "Without deposits and reminders, 20-25% of bookings don't show up. That's money you already counted on.", color: '#f97316' },
    { icon: <BarChart3 size={24} />, title: 'No idea what\'s profitable', description: 'Revenue is in Stripe, expenses in your bank, notes in your phone. You only know if you made money when rent is due.', color: '#eab308' },
    { icon: <Mail size={24} />, title: 'Manual follow-ups fall through', description: 'You mean to send that follow-up email. You forget. Three potential customers, gone.', color: '#ef4444' },
  ];

  return (
    <div style={{ padding: isMobile ? '60px 0' : '100px 0', background: 'transparent' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 64 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 44, fontWeight: 800, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.1 }}>
            Sound familiar?
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textMuted, maxWidth: 500, margin: '0 auto' }}>
            Every small business owner loses money to these problems. Most just accept it.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(2, 1fr)', gap: isMobile ? 16 : 20 }}>
          {pains.map((pain, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: 14,
                border: '1.5px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 20 : 28,
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                <div style={{ color: pain.color, marginTop: 2, flexShrink: 0 }}>{pain.icon}</div>
                <div>
                  <h3 style={{ fontSize: isMobile ? 17 : 19, fontWeight: 700, color: styles.textPrimary, marginBottom: 6, margin: 0 }}>{pain.title}</h3>
                  <p style={{ fontSize: isMobile ? 14 : 15, color: styles.textMuted, margin: 0, lineHeight: 1.6 }}>{pain.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function HowItWorksSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const { isMobile, isTablet } = useResponsive();

  const steps = [
    { number: '1', title: 'Connect your tools', description: 'Gmail, Calendar, Sheets, Stripe, Slack, Twilio, Airtable — one-click OAuth. Takes 30 seconds.', icon: <Zap size={24} /> },
    { number: '2', title: 'Tell Aivaro what to do', description: 'Describe your workflow in plain English or pick a ready-made template. Aivaro asks the right questions — deposit amounts, email tone, who to notify — then builds it.', icon: <MessageSquare size={24} /> },
    { number: '3', title: 'It learns & runs 24/7', description: 'Aivaro stores your pricing, policies, and preferences in a knowledge base. Workflows trigger on emails, schedules, or webhooks — automatically.', icon: <TrendingUp size={24} /> },
  ];

  return (
    <div id="how-it-works" style={{ padding: isMobile ? '60px 0' : '100px 0', background: 'transparent' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 64 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 44, fontWeight: 800, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.1 }}>
            Running in 10 minutes. Not 10 days.
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textMuted }}>
            No consultants. No developers. No 47-page setup guide.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', gap: isMobile ? 16 : 24 }}>
          {steps.map((step, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                borderRadius: 16,
                border: '1.5px solid rgba(139, 92, 246, 0.2)',
                padding: isMobile ? 24 : 32,
                position: 'relative',
              }}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: i * 0.15 }}
              whileHover={{ borderColor: 'rgba(139, 92, 246, 0.5)', y: -4 }}
            >
              <div style={{
                width: 48, height: 48, borderRadius: '50%',
                background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 20, boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
              }}>
                <span style={{ color: '#fff', fontSize: 22, fontWeight: 700 }}>{step.number}</span>
              </div>
              <h3 style={{ fontSize: isMobile ? 19 : 22, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>{step.title}</h3>
              <p style={{ fontSize: isMobile ? 14 : 16, color: styles.textSecondary, margin: 0, lineHeight: 1.6 }}>{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ResultsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const { isMobile, isTablet } = useResponsive();

  return (
    <div id="results" style={{ padding: isMobile ? '60px 0' : '100px 0', background: 'transparent' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 64 }}
        >
          <motion.div
            style={{ display: 'inline-block', padding: '8px 16px', borderRadius: 999, background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', marginBottom: 20 }}
          >
            <span style={{ fontSize: 13, color: styles.accent, fontWeight: 600 }}>REAL RESULTS FROM A REAL BUSINESS</span>
          </motion.div>
          <h2 style={{ fontSize: isMobile ? 28 : 44, fontWeight: 800, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.1 }}>
            We built it for a liquidation business first.
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textMuted, maxWidth: 650, margin: '0 auto', lineHeight: 1.6 }}>
            Before Aivaro, everything was manual — booking confirmations, payment collection, reminders, spreadsheets. Here's what changed.
          </p>
        </motion.div>

        {/* Before / After */}
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)', gap: isMobile ? 16 : 24, marginBottom: isMobile ? 40 : 64 }}>
          {/* Before */}
          <motion.div
            style={{
              background: 'rgba(239, 68, 68, 0.06)',
              borderRadius: 16,
              border: '1.5px solid rgba(239, 68, 68, 0.2)',
              padding: isMobile ? 24 : 32,
            }}
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 20 }}>❌ Before Aivaro</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {[
                '6-8 hours/week on manual booking confirmations',
                '20-25% no-show rate',
                'Manual spreadsheet reconciliation',
                'No idea which months were profitable (or why)',
                'Needed technical help for email automation',
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                  <X size={16} style={{ color: '#ef4444', marginTop: 3, flexShrink: 0 }} />
                  <span style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, lineHeight: 1.5 }}>{item}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* After */}
          <motion.div
            style={{
              background: 'rgba(16, 185, 129, 0.06)',
              borderRadius: 16,
              border: '1.5px solid rgba(16, 185, 129, 0.2)',
              padding: isMobile ? 24 : 32,
            }}
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h3 style={{ fontSize: 14, fontWeight: 700, color: styles.accent, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 20 }}>✅ After Aivaro</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {[
                'Bookings confirmed automatically in seconds',
                'No-show rate dropped to 8% (with deposits + reminders)',
                '~5 hours/week saved on operations',
                'Weekly profit reports generated automatically',
                'Zero technical knowledge needed',
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                  <Check size={16} style={{ color: styles.accent, marginTop: 3, flexShrink: 0 }} />
                  <span style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, lineHeight: 1.5 }}>{item}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Key Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', gap: isMobile ? 12 : 20 }}>
          {[
            { value: '8%', label: 'No-show rate', sublabel: 'Down from 25%' },
            { value: '5h+', label: 'Saved weekly', sublabel: 'Per person' },
            { value: '<2min', label: 'Response time', sublabel: 'Down from 6+ hours' },
            { value: '24/7', label: 'Runs automatically', sublabel: 'While you sleep' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(139, 92, 246, 0.08)',
                borderRadius: 14,
                border: '1px solid rgba(139, 92, 246, 0.2)',
                padding: isMobile ? 20 : 28,
                textAlign: 'center',
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.3 + i * 0.1 }}
            >
              <div style={{ fontSize: isMobile ? 28 : 40, fontWeight: 800, background: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: 4 }}>{stat.value}</div>
              <div style={{ fontSize: isMobile ? 13 : 15, color: styles.textPrimary, fontWeight: 600, marginBottom: 2 }}>{stat.label}</div>
              <div style={{ fontSize: isMobile ? 11 : 13, color: styles.textMuted }}>{stat.sublabel}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function WhatItAutomates() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const { isMobile, isTablet } = useResponsive();

  const workflows = [
    { icon: <Calendar size={24} />, title: 'Booking → Deposit → Reminder', description: 'Collect deposits via Stripe when someone books, send SMS or email reminders before their appointment, track no-shows automatically.', gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' },
    { icon: <Mail size={24} />, title: 'Lead → Follow-up → Close', description: 'Auto-reply to inquiries via email or WhatsApp, send follow-up sequences on a schedule, notify your team on Slack when someone is ready to buy.', gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' },
    { icon: <DollarSign size={24} />, title: 'Payment → Invoice → Report', description: 'Create Stripe payment links and invoices, log transactions to Sheets or Airtable, get automated profit summaries.', gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' },
    { icon: <Bot size={24} />, title: 'AI Agent → Smart Replies', description: 'AI reads your emails and generates context-aware replies using your business knowledge base. It knows your pricing, policies, and tone.', gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)' },
    { icon: <Bell size={24} />, title: 'Schedule → Trigger → Notify', description: 'Run workflows on a schedule — daily reports, weekly summaries, monthly invoices. Set the time and timezone, Aivaro handles the rest.', gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' },
    { icon: <MessageSquare size={24} />, title: 'Custom → Whatever You Need', description: 'Describe any business workflow in plain English. Aivaro asks the right questions, builds it precisely, and runs it 24/7.', gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)' },
  ];

  return (
    <div style={{ padding: isMobile ? '60px 0' : '100px 0', background: 'transparent' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 64 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 44, fontWeight: 800, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.1 }}>
            Revenue loops that run themselves
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textMuted, maxWidth: 550, margin: '0 auto' }}>
            Not a blank canvas. Workflows designed around how small businesses actually make money.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)', gap: isMobile ? 16 : 20 }}>
          {workflows.map((wf, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                borderRadius: 16,
                border: '1.5px solid rgba(255, 255, 255, 0.1)',
                padding: isMobile ? 24 : 32,
                cursor: 'pointer',
              }}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              whileHover={{ scale: 1.02, borderColor: 'rgba(139, 92, 246, 0.5)', boxShadow: '0 10px 40px rgba(139, 92, 246, 0.2)' }}
            >
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: wf.gradient,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'white', marginBottom: 20,
                boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
              }}>
                {wf.icon}
              </div>
              <h3 style={{ fontSize: isMobile ? 18 : 20, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>{wf.title}</h3>
              <p style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, margin: 0, lineHeight: 1.6 }}>{wf.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Integrations inline */}
        <motion.div
          style={{ marginTop: isMobile ? 40 : 64, textAlign: 'center' }}
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          <p style={{ fontSize: 14, color: styles.textMuted, marginBottom: 20 }}>Connects with the tools you already use:</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 12 }}>
            {[
              { name: 'Gmail', icon: '/icons/gmail.svg' },
              { name: 'Google Calendar', icon: '/icons/calendar.svg' },
              { name: 'Google Sheets', icon: '/icons/sheets.svg' },
              { name: 'Stripe', icon: '/icons/stripe.svg' },
              { name: 'Slack', icon: '/icons/slack.svg' },
              { name: 'Twilio SMS', icon: '/icons/twilio.svg' },
              { name: 'Airtable', icon: '/icons/airtable.svg' },
              { name: 'Notion', icon: '/icons/notion.svg' },
              { name: 'Calendly', icon: '/icons/calendly.svg' },
              { name: 'Mailchimp', icon: '/icons/mailchimp.svg' },
            ].map((tool, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '10px 16px', borderRadius: 10,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.1)',
              }}>
                <img src={tool.icon} alt={tool.name} style={{ width: 20, height: 20 }} onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                <span style={{ fontSize: 14, color: styles.textPrimary, fontWeight: 500 }}>{tool.name}</span>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 13, color: styles.textMuted, marginTop: 12 }}>More integrations being added regularly.</p>
        </motion.div>
      </div>
    </div>
  );
}

function PricingSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const { isMobile, isTablet } = useResponsive();

  const plans = [
    {
      name: 'Free Trial',
      price: '$0',
      period: '/7 days',
      description: 'See the magic — no credit card required',
      features: ['1 active workflow', '10 workflow runs', 'Unlimited knowledge entries', 'Core integrations (Gmail, Sheets, Calendar)', 'Email & schedule triggers', 'Template library'],
      limitations: ['No AI agent tasks', 'No file import', 'No Stripe integration'],
      cta: 'Start Free Trial',
      popular: false,
    },
    {
      name: 'Growth',
      price: null,
      period: '',
      description: 'For growing businesses automating more',
      features: ['3 users', '10 active workflows', 'Unlimited runs', 'All integrations (incl. Stripe, Twilio)', 'AI agent tasks', 'File import to knowledge base', 'Scheduled & email triggers', 'Template library', 'Approval workflows', 'Priority support'],
      limitations: [],
      cta: 'Contact Us',
      popular: true,
    },
    {
      name: 'Pro',
      price: null,
      period: '',
      description: 'For teams scaling operations',
      features: ['10 users', 'Unlimited workflows', 'Unlimited runs', 'All integrations', 'Advanced analytics', 'Dedicated support', 'Custom triggers', 'Webhook triggers'],
      limitations: [],
      cta: 'Contact Us',
      popular: false,
    },
  ];

  return (
    <div id="pricing" style={{ padding: isMobile ? '60px 0' : '100px 0', background: 'transparent' }}>
      <div ref={ref} style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 64 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 44, fontWeight: 800, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.1 }}>
            Flexible plans for every stage
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textMuted }}>
            Start with a free trial. Scale as you grow.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', gap: isMobile ? 20 : 24 }}>
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              style={{
                background: plan.popular ? 'rgba(139, 92, 246, 0.08)' : 'rgba(255, 255, 255, 0.03)',
                borderRadius: 20,
                border: plan.popular ? '2px solid rgba(139, 92, 246, 0.5)' : '1.5px solid rgba(255, 255, 255, 0.1)',
                padding: isMobile ? 24 : 36,
                position: 'relative',
                boxShadow: plan.popular ? '0 0 40px rgba(139, 92, 246, 0.15)' : 'none',
              }}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              whileHover={{ y: -6, borderColor: plan.popular ? 'rgba(139, 92, 246, 0.7)' : 'rgba(139, 92, 246, 0.3)' }}
            >
              {plan.popular && (
                <div style={{ position: 'absolute', top: -12, left: '50%', transform: 'translateX(-50%)', background: styles.primary, color: '#fff', padding: '4px 16px', borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                  Most Popular
                </div>
              )}
              <h3 style={{ fontSize: 22, fontWeight: 700, color: styles.textPrimary, marginBottom: 4 }}>{plan.name}</h3>
              <p style={{ fontSize: 14, color: styles.textMuted, marginBottom: 20 }}>{plan.description}</p>
              <div style={{ marginBottom: 24 }}>
                {plan.price ? (
                  <>
                    <span style={{ fontSize: 44, fontWeight: 800, color: styles.textPrimary }}>{plan.price}</span>
                    <span style={{ fontSize: 16, color: styles.textMuted }}>{plan.period}</span>
                  </>
                ) : (
                  <span style={{ fontSize: 20, fontWeight: 600, color: styles.primary }}>Contact us for pricing</span>
                )}
              </div>
              <ul style={{ listStyle: 'none', padding: 0, marginBottom: 12 }}>
                {plan.features.map((f, j) => (
                  <li key={j} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                    <Check size={16} style={{ color: styles.accent, flexShrink: 0 }} />
                    <span style={{ fontSize: 14, color: styles.textSecondary }}>{f}</span>
                  </li>
                ))}
              </ul>
              {plan.limitations && plan.limitations.length > 0 && (
                <ul style={{ listStyle: 'none', padding: 0, marginBottom: 28 }}>
                  {plan.limitations.map((l: string, j: number) => (
                    <li key={j} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <X size={14} style={{ color: '#9ca3af', flexShrink: 0 }} />
                      <span style={{ fontSize: 13, color: '#9ca3af' }}>{l}</span>
                    </li>
                  ))}
                </ul>
              )}
              {!plan.limitations?.length && <div style={{ marginBottom: 28 }} />}
              <Link href="/signup" style={{ textDecoration: 'none' }}>
                <motion.div
                  style={{
                    width: '100%',
                    background: plan.popular ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : 'transparent',
                    color: plan.popular ? '#fff' : styles.primary,
                    padding: '14px 24px',
                    borderRadius: 10,
                    fontSize: 16,
                    fontWeight: 600,
                    border: plan.popular ? 'none' : `2px solid ${styles.primary}`,
                    cursor: 'pointer',
                    textAlign: 'center',
                    boxShadow: plan.popular ? '0 4px 20px rgba(139, 92, 246, 0.4)' : 'none',
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
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
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const { isMobile, isTablet } = useResponsive();

  return (
    <div style={{ padding: isMobile ? '48px 0' : '80px 0', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <motion.div
          ref={ref}
          style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(99, 102, 241, 0.08))',
            borderRadius: 20,
            border: '1.5px solid rgba(139, 92, 246, 0.3)',
            padding: isMobile ? 32 : 56,
            textAlign: 'center',
          }}
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 style={{ fontSize: isMobile ? 26 : 40, fontWeight: 800, color: styles.textPrimary, marginBottom: 12 }}>
            Your next missed lead costs more than trying Aivaro
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textSecondary, marginBottom: 28, maxWidth: 550, margin: '0 auto 28px' }}>
            Free for 7 days. First workflow running in 10 minutes. No credit card required.
          </p>
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <motion.div
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                color: '#fff', padding: isMobile ? '16px 28px' : '18px 36px',
                borderRadius: 10, fontSize: isMobile ? 16 : 18, fontWeight: 700,
                cursor: 'pointer', boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
              }}
              whileHover={{ scale: 1.05, boxShadow: '0 6px 30px rgba(139, 92, 246, 0.6)' }}
              whileTap={{ scale: 0.95 }}
            >
              Start Automating Free
              <ArrowRight size={20} />
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
    <div style={{ padding: isMobile ? '32px 0' : '48px 0', borderTop: '1px solid rgba(139, 92, 246, 0.15)' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: isMobile ? '0 16px' : isTablet ? '0 32px' : '0 64px' }}>
        <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', justifyContent: 'space-between', gap: 16 }}>
          <div>
            <Logo small />
            <p style={{ fontSize: 13, color: styles.textMuted, marginTop: 8 }}>Automate your business. Keep your sanity.</p>
          </div>
          <div style={{ display: 'flex', gap: 24 }}>
            {[
              { label: 'Privacy', href: '/privacy' },
              { label: 'Terms', href: '/terms' },
            ].map((item) => (
              <Link key={item.label} href={item.href} style={{ fontSize: 14, color: styles.textMuted, textDecoration: 'none' }}>
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
  useEffect(() => {
    const styleId = 'aivaro-landing-styles';
    if (!document.getElementById(styleId)) {
      const styleSheet = document.createElement('style');
      styleSheet.id = styleId;
      styleSheet.textContent = `
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `;
      document.head.appendChild(styleSheet);
    }
  }, []);

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
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(139, 92, 246, 0.12), transparent 50%)' }} />
        <div style={{ position: 'absolute', top: '-10%', left: '20%', width: '800px', height: '800px', background: 'radial-gradient(circle, #8b5cf6 0%, transparent 70%)', filter: 'blur(120px)', opacity: 0.2 }} />
        <div style={{ position: 'absolute', top: '40%', right: '-5%', width: '500px', height: '500px', background: 'radial-gradient(circle, #3b82f6 0%, transparent 70%)', filter: 'blur(100px)', opacity: 0.15 }} />
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
      </div>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        <Header />
        <HeroSection />
        <PainSection />
        <HowItWorksSection />
        <ResultsSection />
        <WhatItAutomates />
        <PricingSection />
        <CTASection />
        <Footer />
      </div>
    </div>
  );
}

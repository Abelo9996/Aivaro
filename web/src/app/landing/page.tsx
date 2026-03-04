'use client';
import PageTransition from '@/components/PageTransition';

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { ArrowRight, Zap, Shield, Clock, Check, Bot, Mail, DollarSign, Calendar, Bell, Menu, X, MessageSquare, ChevronDown, CreditCard, Phone, Users, FileText, ShieldCheck, Play, Link2, Brain, Workflow, FormInput } from 'lucide-react';

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
        <div style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '8px 20px' : isTablet ? '8px 40px' : '8px 80px' }}>
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
                {['how-it-works', 'see-it-work', 'results', 'pricing'].map((item) => (
                  <motion.a
                    key={item}
                    href={`#${item}`}
                    onClick={(e) => { e.preventDefault(); smoothScrollTo(item); }}
                    style={{ color: styles.textMuted, fontSize: 14, fontWeight: 500, textDecoration: 'none', cursor: 'pointer', textTransform: 'capitalize' }}
                    whileHover={{ color: styles.textPrimary, scale: 1.05 }}
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
                    whileHover={{ color: styles.textPrimary, scale: 1.05 }}
                  >
                    Sign in
                  </motion.div>
                </Link>
                <Link href="/signup" style={{ textDecoration: 'none' }}>
                  <motion.div
                    style={{ background: styles.primary, color: '#ffffff', padding: '8px 20px', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
                    whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(139, 92, 246, 0.4)' }}
whileTap={{ scale: 0.95 }}
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
            {['how-it-works', 'see-it-work', 'results', 'pricing'].map((item) => (
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
      <div style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '64px 20px 48px' : isTablet ? '80px 40px 64px' : '120px 80px 80px' }}>
        <motion.div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>

          <motion.div
            style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 999, border: '1px solid rgba(16, 185, 129, 0.35)', background: 'rgba(16, 185, 129, 0.08)', marginBottom: isMobile ? 24 : 32 }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', display: 'inline-block', animation: 'pulse 2s ease-in-out infinite' }} />
            <span style={{ fontSize: 13, color: '#6ee7b7', fontWeight: 500 }}>Now in early access</span>
          </motion.div>

          <motion.h1
            style={{ fontSize: isMobile ? 36 : isTablet ? 52 : 72, lineHeight: 1.05, letterSpacing: '-1.5px', fontWeight: 700, color: styles.textPrimary, margin: '0 0 20px', maxWidth: 900 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            An AI employee that{' '}
            <span style={{
              background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 40%, #10b981 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              runs your operations
            </span>
          </motion.h1>

          <motion.p
            style={{ fontSize: isMobile ? 17 : 19, lineHeight: 1.6, color: styles.textMuted, margin: '0 0 36px', maxWidth: 640 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Describe what you need in plain English. Aivaro builds the workflow, connects your tools, and runs it 24/7 - asking permission before anything sensitive.
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
                whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(139, 92, 246, 0.4)' }}
whileTap={{ scale: 0.95 }}
              >
                Start Free Trial
                <ArrowRight size={18} />
              </motion.div>
            </Link>
            <Link href="/demo" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{ color: styles.textSecondary, padding: '14px 32px', borderRadius: 10, fontSize: 16, fontWeight: 500, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8, border: '1px solid rgba(255,255,255,0.12)', width: isMobile ? '100%' : 'auto' }}
                whileHover={{ borderColor: 'rgba(255,255,255,0.35)', scale: 1.03, boxShadow: '0 0 20px rgba(255,255,255,0.05)' }}
whileTap={{ scale: 0.96 }}
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
            style={{ width: '100%', maxWidth: 840, marginTop: isMobile ? 40 : 56 }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5 }}
          >
            <div style={{
              background: 'rgba(10, 10, 30, 0.92)', backdropFilter: 'blur(12px)',
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

function IntegrationLogosSection() {
  const { isMobile } = useResponsive();
  const integrations = [
    { name: 'Gmail', src: '/icons/gmail.svg' },
    { name: 'Google Calendar', src: '/icons/calendar.svg' },
    { name: 'Stripe', src: '/icons/stripe.svg' },
    { name: 'Twilio', src: '/icons/twilio.svg' },
    { name: 'Slack', src: '/icons/slack.svg' },
    { name: 'Airtable', src: '/icons/airtable.svg' },
    { name: 'Notion', src: '/icons/notion.svg' },
    { name: 'Calendly', src: '/icons/calendly.svg' },
    { name: 'Mailchimp', src: '/icons/mailchimp.svg' },
    { name: 'HubSpot', src: '/icons/hubspot.svg' },
    { name: 'Shopify', src: '/icons/shopify.svg' },
    { name: 'Discord', src: '/icons/discord.svg' },
    { name: 'Jira', src: '/icons/jira.svg' },
    { name: 'GitHub', src: '/icons/github.svg' },
    { name: 'Linear', src: '/icons/linear.svg' },
    { name: 'Monday', src: '/icons/monday.svg' },
    { name: 'SendGrid', src: '/icons/sendgrid.svg' },
    { name: 'WhatsApp', src: '/icons/whatsapp.svg' },
    { name: 'Brevo', src: '/icons/brevo.svg' },
  ];

  // Duplicate for seamless infinite loop
  const doubled = [...integrations, ...integrations];
  const itemWidth = isMobile ? 72 : 100;
  const gap = isMobile ? 16 : 28;
  const totalWidth = integrations.length * (itemWidth + gap);
  const duration = integrations.length * 2.5; // seconds for one full cycle

  return (
    <div style={{ padding: isMobile ? '32px 0 0' : '48px 0 0' }}>
      <div style={{ maxWidth: 1800, margin: '0 auto', textAlign: 'center' }}>
        <p style={{ fontSize: 13, color: styles.textMuted, marginBottom: 20, textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 500, padding: '0 20px' }}>
          Works with the tools you already use
        </p>
        <div style={{ overflow: 'hidden', width: '100%', maskImage: 'linear-gradient(to right, transparent, black 8%, black 92%, transparent)', WebkitMaskImage: 'linear-gradient(to right, transparent, black 8%, black 92%, transparent)' }}>
          <motion.div
            style={{ display: 'flex', gap, width: 'max-content' }}
            animate={{ x: [0, -totalWidth] }}
            transition={{ x: { repeat: Infinity, repeatType: 'loop', duration, ease: 'linear' } }}
          >
            {doubled.map((int, i) => (
              <div
                key={`${int.name}-${i}`}
                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, width: itemWidth, flexShrink: 0, opacity: 0.75 }}
              >
                <img
                  src={int.src}
                  alt={int.name}
                  style={{ width: isMobile ? 28 : 36, height: isMobile ? 28 : 36, objectFit: 'contain', filter: 'brightness(0) invert(1)', opacity: 0.8 }}
                />
                <span style={{ fontSize: 11, color: styles.textMuted, whiteSpace: 'nowrap' }}>{int.name}</span>
              </div>
            ))}
          </motion.div>
        </div>
        <p style={{ fontSize: 12, color: styles.textMuted, marginTop: 16, opacity: 0.6, padding: '0 20px' }}>
          19 integrations and counting
        </p>
      </div>
    </div>
  );
}

function DemoShowcaseSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();
  const [activeDemo, setActiveDemo] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const demos = [
    {
      id: 'forms',
      title: 'Smart Form Collection',
      description: 'Collect customer info through chat. Aivaro asks the right questions and fills in the workflow.',
      icon: <FormInput size={18} />,
      video: '/demos/Chat_Form_Input.mp4',
      color: '#fb923c',
      bgColor: 'rgba(251, 146, 60, 0.12)',
    },
    {
      id: 'workflow',
      title: 'Build Workflows in Chat',
      description: 'Describe what you need in plain English. Aivaro creates the entire workflow instantly.',
      icon: <MessageSquare size={18} />,
      video: '/demos/Chat_Workflow_Creation.mp4',
      color: '#38bdf8',
      bgColor: 'rgba(56, 189, 248, 0.12)',
    },
    {
      id: 'visualizer',
      title: 'Visual Workflow Editor',
      description: 'See your workflows as visual flowcharts. Inspect, edit, and understand every step.',
      icon: <Workflow size={18} />,
      video: '/demos/Workflows_Visualizer.mp4',
      color: '#f472b6',
      bgColor: 'rgba(244, 114, 182, 0.12)',
    },
    {
      id: 'knowledge',
      title: 'AI Knowledge Base',
      description: 'Teach Aivaro your business - pricing, policies, tone. Every response sounds like you.',
      icon: <Brain size={18} />,
      video: '/demos/Chat_Knowledge_Base.mp4',
      color: '#6ee7b7',
      bgColor: 'rgba(16, 185, 129, 0.12)',
    },
    {
      id: 'connect',
      title: 'Connect Your Tools',
      description: 'One-click OAuth setup for Gmail, Stripe, Slack, and more. No API keys, no docs.',
      icon: <Link2 size={18} />,
      video: '/demos/Tool_Connection.mp4',
      color: '#a78bfa',
      bgColor: 'rgba(139, 92, 246, 0.12)',
    },
  ];

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const switchDemo = (index: number) => {
    setActiveDemo(index);
    // Reset auto-advance timer on manual click
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % demos.length);
    }, 8000);
  };

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(() => {});
    }
  }, [activeDemo]);

  // Auto-advance every 8 seconds
  useEffect(() => {
    timerRef.current = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % demos.length);
    }, 8000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [demos.length]);

  const active = demos[activeDemo];

  return (
    <div id="see-it-work" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 32 : 48 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            See it in{' '}
            <span style={{ background: 'linear-gradient(135deg, #a78bfa, #10b981)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              action
            </span>
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted }}>
            Real product. Real workflows. No smoke and mirrors.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.15 }}
          style={{
            background: 'rgba(10, 10, 30, 0.92)',
            backdropFilter: 'blur(12px)',
            borderRadius: 16,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            overflow: 'hidden',
          }}
        >
          {/* Tab bar */}
          <div style={{
            display: 'flex',
            overflowX: 'auto',
            borderBottom: '1px solid rgba(255,255,255,0.06)',
            padding: '0 4px',
            gap: 0,
            scrollbarWidth: 'none',
          }}>
            {demos.map((demo, i) => (
              <motion.button
                key={demo.id}
                onClick={() => switchDemo(i)}
                style={{
                  flex: isMobile ? 'none' : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  padding: isMobile ? '14px 16px' : '16px 20px',
                  background: 'transparent',
                  border: 'none',
                  borderBottom: i === activeDemo ? `2px solid ${demo.color}` : '2px solid transparent',
                  color: i === activeDemo ? demo.color : styles.textMuted,
                  cursor: 'pointer',
                  fontSize: isMobile ? 12 : 13,
                  fontWeight: i === activeDemo ? 600 : 500,
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s',
                  minWidth: isMobile ? 'auto' : 0,
                }}
                whileHover={{ color: demo.color, background: 'rgba(255,255,255,0.03)' }}
              >
                <span style={{ display: 'flex', alignItems: 'center', opacity: i === activeDemo ? 1 : 0.6 }}>{demo.icon}</span>
                {!isMobile && <span>{demo.title}</span>}
                {isMobile && <span style={{ fontSize: 11 }}>{demo.title.split(' ').slice(0, 2).join(' ')}</span>}
              </motion.button>
            ))}
          </div>

          {/* Video + description area */}
          <div style={{
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
          }}>
            {/* Video */}
            <div style={{
              flex: isMobile ? 'none' : '1 1 65%',
              position: 'relative',
              background: 'rgba(10, 10, 30, 1)',
              minHeight: isMobile ? 220 : 400,
              overflow: 'hidden',
            }}>
              <AnimatePresence mode="popLayout">
                <motion.video
                  ref={videoRef}
                  key={active.video}
                  src={active.video}
                  autoPlay
                  loop
                  muted
                  playsInline
                  initial={{ opacity: 0, scale: 1.02 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.5, ease: 'easeInOut' }}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    maxHeight: isMobile ? 260 : 450,
                  }}
                />
              </AnimatePresence>
            </div>

            {/* Description sidebar */}
            <div style={{
              flex: isMobile ? 'none' : '0 0 35%',
              padding: isMobile ? '20px 20px 24px' : '32px 28px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              borderLeft: isMobile ? 'none' : '1px solid rgba(255,255,255,0.06)',
              borderTop: isMobile ? '1px solid rgba(255,255,255,0.06)' : 'none',
            }}>
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeDemo}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.35, ease: 'easeInOut' }}
                >
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: 8,
                  padding: '6px 12px', borderRadius: 8,
                  background: active.bgColor,
                  marginBottom: 16,
                }}>
                  <span style={{ color: active.color, display: 'flex', alignItems: 'center' }}>{active.icon}</span>
                  <span style={{ fontSize: 13, fontWeight: 600, color: active.color }}>{active.title}</span>
                </div>
                <p style={{
                  fontSize: isMobile ? 15 : 17,
                  color: styles.textSecondary,
                  lineHeight: 1.7,
                  margin: '0 0 20px',
                }}>
                  {active.description}
                </p>

                {/* Progress dots */}
                <div style={{ display: 'flex', gap: 6 }}>
                  {demos.map((_, i) => (
                    <motion.div
                      key={i}
                    onClick={() => switchDemo(i)}
                      style={{
                        width: i === activeDemo ? 24 : 8,
                        height: 8,
                        borderRadius: 4,
                        background: i === activeDemo ? active.color : 'rgba(255,255,255,0.15)',
                        cursor: 'pointer',
                        transition: 'all 0.3s',
                      }}
                      whileHover={{ background: i === activeDemo ? active.color : 'rgba(255,255,255,0.3)' }}
                    />
                  ))}
                </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function TemplateGallerySection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const templates = [
    {
      icon: <Calendar size={20} />,
      name: 'Appointment Reminders',
      description: 'Automatically send SMS and email reminders before appointments. Reduce no-shows by up to 70%.',
      integrations: ['Twilio', 'Gmail', 'Google Calendar'],
      timeSaved: '3 hrs/week',
      color: 'rgba(139, 92, 246, 0.15)',
      iconColor: '#a78bfa',
    },
    {
      icon: <CreditCard size={20} />,
      name: 'Invoice & Payment Collection',
      description: 'Send Stripe payment links after booking. Auto-follow-up on unpaid invoices.',
      integrations: ['Stripe', 'Gmail'],
      timeSaved: '2 hrs/week',
      color: 'rgba(16, 185, 129, 0.15)',
      iconColor: '#6ee7b7',
    },
    {
      icon: <Users size={20} />,
      name: 'New Lead Auto-Response',
      description: 'Instantly respond to new leads via email with personalized messages that match your voice.',
      integrations: ['Gmail', 'Airtable'],
      timeSaved: '4 hrs/week',
      color: 'rgba(251, 146, 60, 0.15)',
      iconColor: '#fb923c',
    },
    {
      icon: <FileText size={20} />,
      name: 'Weekly Business Report',
      description: 'Get a summary of your week - new bookings, revenue, and follow-ups - delivered every Monday.',
      integrations: ['Gmail', 'Airtable', 'Stripe'],
      timeSaved: '1 hr/week',
      color: 'rgba(56, 189, 248, 0.15)',
      iconColor: '#38bdf8',
    },
    {
      icon: <MessageSquare size={20} />,
      name: 'Customer Follow-Up',
      description: 'Automatically check in with customers after service. Request reviews and build loyalty.',
      integrations: ['Gmail', 'Twilio'],
      timeSaved: '2 hrs/week',
      color: 'rgba(244, 114, 182, 0.15)',
      iconColor: '#f472b6',
    },
  ];

  return (
    <div id="templates" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 56 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            Start with a{' '}
            <span style={{ background: 'linear-gradient(135deg, #a78bfa, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              proven template
            </span>
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted }}>
            One click to deploy. Customize with plain English.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)', gap: isMobile ? 12 : 16 }}>
          {templates.slice(0, isMobile ? 3 : isTablet ? 4 : 5).map((t, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(10, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 20 : 24,
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ type: 'spring', stiffness: 300, damping: 20, delay: i * 0.08 }}
              whileHover={{ borderColor: 'rgba(139, 92, 246, 0.4)', y: -4, boxShadow: '0 8px 30px rgba(139, 92, 246, 0.15)' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: t.color, display: 'flex', alignItems: 'center', justifyContent: 'center', color: t.iconColor }}>
                  {t.icon}
                </div>
                <div>
                  <h3 style={{ fontSize: 15, fontWeight: 600, color: styles.textPrimary, margin: 0 }}>{t.name}</h3>
                  <span style={{ fontSize: 12, color: styles.accent, fontWeight: 500 }}>Saves ~{t.timeSaved}</span>
                </div>
              </div>
              <p style={{ fontSize: 13, color: styles.textMuted, margin: '0 0 14px', lineHeight: 1.6 }}>{t.description}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {t.integrations.map((int, j) => (
                  <span key={j} style={{ fontSize: 11, padding: '3px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', color: styles.textMuted }}>
                    {int}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
          style={{ textAlign: 'center', marginTop: 32 }}
        >
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <motion.span
              style={{ fontSize: 14, color: styles.primaryLight, fontWeight: 500, cursor: 'pointer' }}
              whileHover={{ color: styles.textPrimary, scale: 1.05 }}
            >
              Browse all templates →
            </motion.span>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}

function ApprovalFeatureSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  return (
    <div style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)', gap: isMobile ? 32 : 64, alignItems: 'center', background: 'rgba(10, 10, 30, 0.85)', backdropFilter: 'blur(12px)', borderRadius: 16, border: '1px solid rgba(255, 255, 255, 0.08)', padding: isMobile ? 24 : 40 }}>
          {/* Left - Copy */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5 }}
          >
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 12px', borderRadius: 999, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', marginBottom: 16 }}>
              <ShieldCheck size={14} color={styles.accent} />
              <span style={{ fontSize: 12, color: styles.accent, fontWeight: 500 }}>Built-in guardrails</span>
            </div>
            <h2 style={{ fontSize: isMobile ? 28 : 36, fontWeight: 700, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.15 }}>
              AI that asks before it acts
            </h2>
            <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted, lineHeight: 1.7, marginBottom: 24 }}>
              Payments, external emails, and SMS messages automatically require your approval. You stay in control - Aivaro never sends money or contacts customers without your OK.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                'Payments and invoices need your approval',
                'External emails reviewed before sending',
                'SMS and calls gated by default',
                'Toggle approval on any workflow step',
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 20, height: 20, borderRadius: 6, background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Check size={12} color={styles.accent} />
                  </div>
                  <span style={{ fontSize: 14, color: styles.textSecondary }}>{item}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right - Approval mockup */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.15 }}
          >
            <div style={{
              background: 'rgba(10, 10, 30, 0.92)', backdropFilter: 'blur(12px)',
              borderRadius: 14,
              border: '1px solid rgba(255, 255, 255, 0.1)',
              overflow: 'hidden',
            }}>
              {/* Header */}
              <div style={{ padding: '12px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b', animation: 'pulse 2s ease-in-out infinite' }} />
                <span style={{ fontSize: 12, color: '#f59e0b', fontWeight: 500 }}>Approval Required</span>
              </div>
              {/* Content */}
              <div style={{ padding: 20 }}>
                <p style={{ fontSize: 14, color: styles.textSecondary, margin: '0 0 16px', lineHeight: 1.6 }}>
                  <span style={{ fontWeight: 600, color: styles.textPrimary }}>Send Invoice</span> wants to charge{' '}
                  <span style={{ fontWeight: 600, color: styles.textPrimary }}>$500.00</span> via Stripe to:
                </p>
                <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: 14, marginBottom: 16, border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ fontSize: 13, color: styles.textMuted }}>Customer</span>
                    <span style={{ fontSize: 13, color: styles.textPrimary }}>john@client.com</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ fontSize: 13, color: styles.textMuted }}>Amount</span>
                    <span style={{ fontSize: 13, color: styles.textPrimary }}>$500.00</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 13, color: styles.textMuted }}>Workflow</span>
                    <span style={{ fontSize: 13, color: styles.textPrimary }}>Post-Booking Deposit</span>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                  <motion.div
                    style={{ flex: 1, background: styles.accent, color: '#fff', padding: '10px 16px', borderRadius: 8, fontSize: 14, fontWeight: 600, textAlign: 'center', cursor: 'pointer' }}
                    whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }}
whileTap={{ scale: 0.95 }}
>
Approve
                  </motion.div>
                  <motion.div
                    style={{ flex: 1, background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', padding: '10px 16px', borderRadius: 8, fontSize: 14, fontWeight: 600, textAlign: 'center', cursor: 'pointer', border: '1px solid rgba(239, 68, 68, 0.2)' }}
                    whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(239, 68, 68, 0.3)' }}
whileTap={{ scale: 0.95 }}
>
Reject
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function HowItWorksSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const steps = [
    { number: '1', title: 'Connect your tools', description: 'Gmail, Calendar, Stripe, Slack, Twilio, Airtable, Notion, Calendly, Mailchimp - one-click setup.', icon: <Zap size={20} /> },
    { number: '2', title: 'Describe what you need', description: 'Tell Aivaro in plain English or pick a template. It asks the right questions, then builds it.', icon: <MessageSquare size={20} /> },
    { number: '3', title: 'It runs 24/7', description: 'Workflows trigger on emails, schedules, or webhooks. Every message matches your voice.', icon: <Bot size={20} /> },
  ];

  return (
    <div id="how-it-works" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
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
                background: 'rgba(10, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 24 : 28,
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.15 }}
              whileHover={{ y: -6, borderColor: 'rgba(139, 92, 246, 0.3)', boxShadow: '0 12px 30px rgba(139, 92, 246, 0.12)' }}
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
    { value: '70%', label: 'Fewer missed follow-ups', detail: 'Automated outreach' },
    { value: '24/7', label: 'Always running', detail: 'Zero manual work' },
  ];

  return (
    <div id="results" style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 56 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : 40, fontWeight: 700, color: styles.textPrimary, marginBottom: 8, lineHeight: 1.1 }}>
            Real results from <span style={{ background: 'linear-gradient(135deg, #10b981, #6ee7b7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>real businesses</span>
          </h2>
          <p style={{ fontSize: isMobile ? 15 : 17, color: styles.textMuted, maxWidth: 500, margin: '0 auto' }}>
            Our first pilot - a liquidation business - cut no-shows by 70% and saved 5+ hours per week on operations.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', gap: isMobile ? 12 : 16, marginBottom: isMobile ? 40 : 56 }}>
          {metrics.map((stat, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(10, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 20 : 24,
                textAlign: 'center',
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.2 + i * 0.08 }}
              whileHover={{ y: -4, borderColor: 'rgba(139, 92, 246, 0.3)', boxShadow: '0 8px 24px rgba(139, 92, 246, 0.1)' }}
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
              background: 'rgba(30, 10, 10, 0.85)', backdropFilter: 'blur(12px)',
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
              background: 'rgba(10, 25, 20, 0.85)', backdropFilter: 'blur(12px)',
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

        {/* Testimonial */}
        <motion.div
          style={{
            marginTop: isMobile ? 32 : 48,
            background: 'rgba(15, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
            borderRadius: 14,
            border: '1px solid rgba(139, 92, 246, 0.15)',
            padding: isMobile ? 24 : 32,
            textAlign: 'center',
          }}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <p style={{ fontSize: isMobile ? 16 : 18, color: styles.textSecondary, lineHeight: 1.7, fontStyle: 'italic', margin: '0 0 16px', maxWidth: 640, marginLeft: 'auto', marginRight: 'auto' }}>
            &ldquo;I used to spend hours every week confirming bookings and chasing people who didn&apos;t show up. Now it&apos;s all automatic - reminders go out, deposits get collected, and my no-show rate dropped from 25% to 8%. I don&apos;t even think about it anymore.&rdquo;
          </p>
          <div>
            <span style={{ fontSize: 14, fontWeight: 600, color: styles.textPrimary }}>David Yagubyan</span>
            <span style={{ fontSize: 13, color: styles.textMuted }}> · Owner, Pacific Liquidation & Auctions</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function FeaturesSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  const { isMobile, isTablet } = useResponsive();

  const features = [
    { icon: <MessageSquare size={20} />, title: 'Natural Language Workflows', description: 'Describe what you need in plain English. Aivaro builds it - no drag-and-drop required.' },
    { icon: <Bot size={20} />, title: 'AI Knowledge Base', description: 'Stores your pricing, policies, and tone. Every message sounds like you wrote it.' },
    { icon: <Shield size={20} />, title: 'Approval Gates', description: 'Sensitive actions (payments, external emails) require your OK before sending.' },
    { icon: <Mail size={20} />, title: 'Personalized Communication', description: 'AI rewrites every email, SMS, and message to match your voice.' },
    { icon: <Zap size={20} />, title: '8 Integrations', description: 'Gmail, Stripe, Twilio, Slack, Airtable, Notion, Calendly, Mailchimp - all connected.' },
    { icon: <Clock size={20} />, title: 'Scheduled Triggers', description: 'Run workflows on a schedule - daily reports, weekly invoices, monthly summaries.' },
  ];

  return (
    <div style={{ padding: isMobile ? '60px 0' : '100px 0' }}>
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
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
                background: 'rgba(10, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
                borderRadius: 14,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 20 : 24,
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              whileHover={{ y: -6, borderColor: 'rgba(139, 92, 246, 0.3)', boxShadow: '0 12px 30px rgba(139, 92, 246, 0.12)' }}
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
      <div ref={ref} style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
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
                background: plan.popular ? 'rgba(20, 12, 40, 0.9)' : 'rgba(10, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
                borderRadius: 14,
                border: plan.popular ? '1.5px solid rgba(139, 92, 246, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)',
                padding: isMobile ? 24 : 28,
                position: 'relative',
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              whileHover={{ y: -8, boxShadow: plan.popular ? '0 16px 40px rgba(139, 92, 246, 0.25)' : '0 12px 30px rgba(139, 92, 246, 0.1)' }}
            >
              {plan.popular && (
                <motion.div
                  style={{ position: 'absolute', top: -10, left: '50%', transform: 'translateX(-50%)', background: styles.primary, color: '#fff', padding: '3px 12px', borderRadius: 999, fontSize: 11, fontWeight: 600 }}
                  animate={{ boxShadow: ['0 0 8px rgba(139, 92, 246, 0.3)', '0 0 20px rgba(139, 92, 246, 0.6)', '0 0 8px rgba(139, 92, 246, 0.3)'] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                >
                  Popular
                </motion.div>
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
                  whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(139, 92, 246, 0.4)' }}
whileTap={{ scale: 0.95 }}
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
      <div style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
        <motion.div
          ref={ref}
          style={{
            background: 'rgba(15, 10, 30, 0.85)', backdropFilter: 'blur(12px)',
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
              whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(139, 92, 246, 0.4)' }}
whileTap={{ scale: 0.95 }}
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
      <div style={{ maxWidth: 1800, margin: '0 auto', padding: isMobile ? '0 20px' : isTablet ? '0 40px' : '0 80px' }}>
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
              <Link key={item.label} href={item.href} style={{ textDecoration: 'none' }}>
                <motion.span
                  style={{ fontSize: 13, color: styles.textMuted, cursor: 'pointer', display: 'inline-block' }}
                  whileHover={{ color: '#e2e8f0', y: -1 }}
                  transition={{ duration: 0.2 }}
                >
                  {item.label}
                </motion.span>
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
    <PageTransition>
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
      `}</style>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        <Header />
        <HeroSection />
        <IntegrationLogosSection />
        <HowItWorksSection />
        <DemoShowcaseSection />
        <TemplateGallerySection />
        <ResultsSection />
        <ApprovalFeatureSection />
        <FeaturesSection />
        <PricingSection />
        <CTASection />
        <Footer />
      </div>
    </div>
    </PageTransition>
  );
}

'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect, useRef } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Zap, Shield, TrendingUp, Clock, Check, Bot, Workflow, Globe, Sparkles, Play, GitBranch, Users } from 'lucide-react';

const styles = {
  primary: '#8b5cf6',        // Purple (Aivaro brand)
  primaryLight: '#a78bfa',   // Lighter Purple
  secondary: '#3b82f6',      // Blue accent
  accent: '#10b981',         // Emerald accent
  cyan: '#06b6d4',           // Cyan highlight
  textPrimary: '#e2e8f0',    // Light slate
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  darkBg: '#0a0a1a',
  darkerBg: '#050510',
  darkText: '#020306',
};

// Smooth scroll utility function
const smoothScrollTo = (elementId: string) => {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }
};

function Logo() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{
        width: 36,
        height: 36,
        background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
        borderRadius: 10,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(139, 92, 246, 0.4)'
      }}>
        <Workflow size={22} color="white" />
      </div>
      <span style={{ 
        fontSize: 24, 
        fontWeight: 800, 
        background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        letterSpacing: '-0.5px'
      }}>
        Aivaro
      </span>
    </div>
  );
}

function Header() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.div
      style={{
        backgroundColor: scrolled ? 'rgba(10, 10, 26, 0.95)' : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
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
      <div style={{ 
        maxWidth: 1440, 
        margin: '0 auto', 
        padding: scrolled ? '8px 48px' : '8px 48px',
        transition: 'all 500ms'
      }}>
        <div style={{
          backdropFilter: scrolled ? 'none' : 'blur(48px)',
          background: scrolled ? 'transparent' : 'rgba(139, 92, 246, 0.08)',
          display: 'flex',
          gap: 96,
          alignItems: 'center',
          padding: '8px 24px',
          borderRadius: scrolled ? 0 : 16,
          boxShadow: scrolled ? 'none' : '0px 4px 24px rgba(0, 0, 0, 0.16)',
          transition: 'all 500ms'
        }}>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <Logo />
            </motion.div>
          </Link>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center', flex: 1 }}>
            {['features', 'how-it-works', 'integrations', 'pricing'].map((item) => (
              <motion.a 
                key={item}
                href={`#${item}`}
                onClick={(e) => {
                  e.preventDefault();
                  smoothScrollTo(item);
                }}
                style={{
                  color: styles.textPrimary,
                  fontSize: 15,
                  fontWeight: 500,
                  textDecoration: 'none',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
                whileHover={{ 
                  color: styles.primary,
                  scale: 1.05
                }}
                transition={{ duration: 0.2 }}
              >
                {item.replace('-', ' ')}
              </motion.a>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <Link href="/login" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{
                  background: 'transparent',
                  color: styles.textPrimary,
                  padding: '8px 16px',
                  borderRadius: 999,
                  fontSize: 15,
                  border: '1.5px solid rgba(139, 92, 246, 0.3)',
                  cursor: 'pointer',
                  display: 'inline-block'
                }}
                whileHover={{ 
                  scale: 1.05,
                  borderColor: 'rgba(139, 92, 246, 0.6)',
                  background: 'rgba(139, 92, 246, 0.1)'
                }}
                whileTap={{ scale: 0.95 }}
              >
                Sign in
              </motion.div>
            </Link>
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: '#ffffff',
                  padding: '8px 16px',
                  borderRadius: 999,
                  fontSize: 15,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-block'
                }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)'
                }}
                whileTap={{ scale: 0.95 }}
              >
                Get Started Free
              </motion.div>
            </Link>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function HeroSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '15%']);
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0.3]);

  return (
    <div ref={ref} style={{ background: 'transparent', position: 'relative', overflow: 'hidden' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '96px 96px' }}>
        <motion.div style={{ display: 'flex', flexDirection: 'column', gap: 48, alignItems: 'center', y, opacity }}>
          <motion.div 
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 16px',
              borderRadius: 999,
              border: `1px solid rgba(139, 92, 246, 0.4)`,
              background: 'rgba(139, 92, 246, 0.1)'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span style={{ fontSize: 14, color: styles.primary, fontWeight: 600 }}>✨ AI-Powered Workflow Automation</span>
          </motion.div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, alignItems: 'center', maxWidth: 900 }}>
            <motion.h1
              style={{
                fontSize: 72,
                lineHeight: 1.1,
                letterSpacing: '-2px',
                fontWeight: 800,
                color: styles.textPrimary,
                textAlign: 'center',
                margin: 0
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Automate Your Business Like{' '}
              <span style={{ 
                background: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                Magic
              </span>
            </motion.h1>
            <motion.p
              style={{
                fontSize: 24,
                lineHeight: '32px',
                color: styles.textPrimary,
                opacity: 0.8,
                textAlign: 'center',
                margin: 0
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              Build powerful automations with a visual editor. Connect your apps, let AI suggest workflows, and save hours every week.
            </motion.p>
          </div>

          <motion.div
            style={{ display: 'flex', gap: 16, alignItems: 'center' }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: '#ffffff',
                  padding: '16px 32px',
                  borderRadius: 8,
                  fontSize: 18,
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)'
                }}
                whileHover={{ scale: 1.05, boxShadow: '0 6px 30px rgba(139, 92, 246, 0.6)' }}
                whileTap={{ scale: 0.95 }}
              >
                Start Building Free
                <ArrowRight size={20} />
              </motion.div>
            </Link>
            <motion.div
              style={{
                background: 'transparent',
                color: styles.primary,
                padding: '16px 32px',
                borderRadius: 8,
                fontSize: 18,
                fontWeight: 600,
                border: `2px solid ${styles.primary}`,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8
              }}
              whileHover={{ 
                scale: 1.05,
                background: 'rgba(139, 92, 246, 0.1)',
                boxShadow: '0 4px 20px rgba(139, 92, 246, 0.3)'
              }}
              whileTap={{ scale: 0.95 }}
            >
              <Play size={20} />
              Watch Demo
            </motion.div>
          </motion.div>

          <motion.p
            style={{ fontSize: 15, color: styles.textMuted, textAlign: 'center', margin: 0 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            No credit card required • Setup in 2 minutes • Cancel anytime
          </motion.p>

          {/* Dashboard Preview */}
          <motion.div
            style={{ width: '100%', maxWidth: 1100, marginTop: 64 }}
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <motion.div
              style={{
                background: 'linear-gradient(135deg, rgba(30, 30, 40, 0.95) 0%, rgba(20, 20, 35, 0.95) 100%)',
                borderRadius: 20,
                border: '2px solid rgba(139, 92, 246, 0.3)',
                overflow: 'hidden',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(139, 92, 246, 0.2)'
              }}
              whileHover={{ 
                scale: 1.01,
                boxShadow: '0 25px 70px rgba(0, 0, 0, 0.6), 0 0 50px rgba(139, 92, 246, 0.3)'
              }}
              transition={{ duration: 0.3 }}
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
                  <Shield size={14} color={styles.primary} />
                  <span>app.aivaro.io/workflows</span>
                </div>
              </div>

              {/* Workflow Editor Preview */}
              <div style={{ padding: '48px 40px' }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 36 }}>
                  <Logo />
                  <span style={{ color: styles.textMuted, marginLeft: 16 }}>Workflow Editor</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
                  {[
                    { label: 'Active Workflows', value: '24', icon: <Workflow size={20} /> },
                    { label: 'Time Saved Weekly', value: '38h', icon: <Clock size={20} /> },
                    { label: 'Tasks Automated', value: '2.4K', icon: <Zap size={20} /> }
                  ].map((stat, i) => (
                    <motion.div
                      key={i}
                      style={{ 
                        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)',
                        padding: '28px 24px', 
                        borderRadius: 16,
                        border: '1.5px solid rgba(139, 92, 246, 0.3)',
                        position: 'relative',
                        overflow: 'hidden'
                      }}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.8 + i * 0.1 }}
                      whileHover={{
                        scale: 1.03,
                        borderColor: 'rgba(139, 92, 246, 0.5)'
                      }}
                    >
                      <div style={{
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        color: styles.primary,
                        opacity: 0.5
                      }}>
                        {stat.icon}
                      </div>
                      
                      <p style={{ 
                        color: styles.textSecondary, 
                        fontSize: 13, 
                        marginBottom: 8, 
                        margin: 0,
                        fontWeight: 500,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}>
                        {stat.label}
                      </p>
                      <p style={{ 
                        color: styles.textPrimary, 
                        fontSize: 36, 
                        fontWeight: 800, 
                        margin: 0,
                        background: `linear-gradient(135deg, ${styles.primary} 0%, ${styles.secondary} 100%)`,
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text'
                      }}>
                        {stat.value}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}

function StatsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const stats = [
    { icon: <Clock size={32} />, value: '10x', label: 'Faster workflow creation' },
    { icon: <Shield size={32} />, value: '50+', label: 'App integrations' },
    { icon: <TrendingUp size={32} />, value: '40hrs', label: 'Saved per month' },
    { icon: <Zap size={32} />, value: '99.9%', label: 'Uptime guaranteed' }
  ];

  return (
    <div style={{ background: 'transparent', padding: '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 48px' }}>
        <motion.div ref={ref} style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 32 }}>
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(10, 10, 26, 0.6)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: 20,
                padding: 32,
                textAlign: 'center'
              }}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: i * 0.1 }}
            >
              <div style={{ color: styles.primary, marginBottom: 16 }}>{stat.icon}</div>
              <div style={{ color: styles.textPrimary, fontSize: 48, fontWeight: 800, marginBottom: 8 }}>{stat.value}</div>
              <div style={{ color: styles.textSecondary, fontSize: 16 }}>{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}

function FeaturesSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  const features = [
    {
      icon: <Workflow size={32} />,
      title: 'Visual Workflow Builder',
      description: 'Drag-and-drop interface to create complex automations without any coding. See your logic flow in real-time.',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    },
    {
      icon: <Bot size={32} />,
      title: 'AI-Powered Suggestions',
      description: 'Describe what you want in plain English, and AI builds the workflow for you. Smart recommendations as you build.',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    },
    {
      icon: <Globe size={32} />,
      title: '50+ Integrations',
      description: 'Connect Google, Slack, Stripe, Notion, and dozens more. OAuth-based secure connections.',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
    {
      icon: <Users size={32} />,
      title: 'Human-in-the-Loop',
      description: 'Add approval steps for sensitive actions. Get notified and approve via email, Slack, or the dashboard.',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
      icon: <GitBranch size={32} />,
      title: 'Conditional Logic',
      description: 'Build branching workflows with if/then logic. Filter, transform, and route data automatically.',
      gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
    },
    {
      icon: <Sparkles size={32} />,
      title: 'Ready-Made Templates',
      description: 'Start from 100+ pre-built templates for common use cases. Customize to fit your exact needs.',
      gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
    },
  ];

  return (
    <div id="features" ref={ref} style={{ 
      padding: '120px 0', 
      background: `linear-gradient(180deg, ${styles.darkBg} 0%, ${styles.darkerBg} 100%)`,
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '-10%',
        width: '500px',
        height: '500px',
        background: 'radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%)',
        filter: 'blur(60px)',
        pointerEvents: 'none'
      }} />

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          style={{ textAlign: 'center', marginBottom: 80 }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            style={{
              display: 'inline-block',
              padding: '10px 24px',
              borderRadius: 999,
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1.5px solid rgba(139, 92, 246, 0.3)',
              marginBottom: 24,
            }}
          >
            <span style={{ color: styles.primary, fontSize: 14, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              ⚡ Powerful Features
            </span>
          </motion.div>
          <h2 style={{ fontSize: 56, fontWeight: 800, color: styles.textPrimary, marginBottom: 20, lineHeight: 1.1 }}>
            Everything You Need to Automate
          </h2>
          <p style={{ fontSize: 20, color: styles.textSecondary, maxWidth: 800, margin: '0 auto', lineHeight: 1.7 }}>
            Build, deploy, and manage workflows that run your business on autopilot
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
          {features.map((feature, index) => (
            <motion.div
              key={index}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                borderRadius: 16,
                border: '1.5px solid rgba(255, 255, 255, 0.2)',
                padding: 32,
                cursor: 'pointer',
              }}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{
                scale: 1.03,
                y: -10,
                boxShadow: '0 20px 50px rgba(139, 92, 246, 0.3)',
                borderColor: 'rgba(139, 92, 246, 0.6)',
                background: 'rgba(139, 92, 246, 0.1)',
              }}
            >
              <div
                style={{ 
                  width: 56,
                  height: 56,
                  borderRadius: 12,
                  background: feature.gradient,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  marginBottom: 24,
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)'
                }}
              >
                {feature.icon}
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>
                {feature.title}
              </h3>
              <p style={{ fontSize: 16, color: styles.textSecondary, margin: 0, lineHeight: 1.6 }}>
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function FeatureShowcaseSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const features = [
    {
      id: 1,
      title: 'Visual Workflow Builder',
      description: 'Drag and drop to create powerful automations. See your logic flow in real-time with an intuitive canvas editor.',
      image: '/images/example_tool_1.png',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
      metrics: [
        { label: 'Node Types', value: '25+', color: '#8b5cf6' },
        { label: 'Build Time', value: '< 5min', color: '#7c3aed' },
        { label: 'No Code', value: '100%', color: '#10b981' },
      ]
    },
    {
      id: 2,
      title: 'AI-Powered Automation',
      description: 'Describe what you want in plain English. AI builds the workflow for you with smart suggestions at every step.',
      image: '/images/example_tool_2.png',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
      metrics: [
        { label: 'Generation', value: '< 3s', color: '#3b82f6' },
        { label: 'Accuracy', value: '95%', color: '#2563eb' },
        { label: 'Languages', value: '10+', color: '#10b981' },
      ]
    },
    {
      id: 3,
      title: 'Smart Approval Workflows',
      description: 'Add human-in-the-loop for sensitive actions. Get notified via email or Slack and approve with one click.',
      image: '/images/example_tool_3.png',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      metrics: [
        { label: 'Channels', value: '5+', color: '#10b981' },
        { label: 'Response', value: '1-click', color: '#059669' },
        { label: 'Audit Log', value: 'Full', color: '#10b981' },
      ]
    },
    {
      id: 4,
      title: 'Unified Integration Hub',
      description: 'Connect all your apps from a single dashboard. OAuth-based secure connections with automatic token refresh.',
      image: '/images/example_tool_4.png',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      metrics: [
        { label: 'Integrations', value: '50+', color: '#f59e0b' },
        { label: 'Setup Time', value: '< 30s', color: '#d97706' },
        { label: 'OAuth', value: 'Secure', color: '#10b981' },
      ]
    }
  ];

  return (
    <div id="showcase" ref={ref} style={{ 
      padding: '120px 0', 
      background: `linear-gradient(180deg, ${styles.darkerBg} 0%, ${styles.darkBg} 100%)`,
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background gradient orbs */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '-10%',
        width: '500px',
        height: '500px',
        background: 'radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%)',
        filter: 'blur(60px)',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute',
        bottom: '10%',
        right: '-10%',
        width: '600px',
        height: '600px',
        background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
        filter: 'blur(60px)',
        pointerEvents: 'none'
      }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          style={{ textAlign: 'center', marginBottom: '80px' }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            style={{
              display: 'inline-block',
              padding: '10px 24px',
              borderRadius: 999,
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1.5px solid rgba(139, 92, 246, 0.3)',
              marginBottom: '24px',
              boxShadow: '0 4px 16px rgba(139, 92, 246, 0.2)'
            }}
          >
            <span style={{ 
              color: styles.primary, 
              fontSize: '14px', 
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase'
            }}>
              🎬 Product Tour
            </span>
          </motion.div>
          <h2 style={{
            fontSize: '56px',
            fontWeight: 800,
            color: styles.textPrimary,
            marginBottom: '20px',
            lineHeight: 1.1,
            letterSpacing: '-0.02em'
          }}>
            See Aivaro in Action
          </h2>
          <p style={{
            fontSize: '20px',
            color: styles.textSecondary,
            maxWidth: '800px',
            margin: '0 auto',
            lineHeight: 1.7
          }}>
            Watch how our visual workflow builder turns complex automations into simple drag-and-drop experiences
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '120px' }}>
          {features.map((feature, index) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 80 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: index * 0.2 }}
            >
              {/* Title and Description */}
              <div style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                  <div style={{
                    display: 'flex',
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: feature.gradient,
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '22px',
                    fontWeight: 700,
                    color: 'white',
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)'
                  }}>
                    {feature.id}
                  </div>
                  <h3 style={{
                    fontSize: '36px',
                    fontWeight: 700,
                    color: styles.textPrimary,
                    lineHeight: 1.2,
                    letterSpacing: '-0.02em'
                  }}>
                    {feature.title}
                  </h3>
                </div>
                <p style={{
                  fontSize: '18px',
                  color: styles.textSecondary,
                  lineHeight: 1.7,
                  maxWidth: '800px'
                }}>
                  {feature.description}
                </p>
              </div>

              {/* Feature Card with Screenshot and Metrics */}
              <motion.div
                style={{
                  background: 'rgba(10, 10, 26, 0.8)',
                  borderRadius: '24px',
                  border: '2px solid rgba(139, 92, 246, 0.3)',
                  overflow: 'hidden',
                  backdropFilter: 'blur(20px)',
                }}
                whileHover={{
                  scale: 1.01,
                  borderColor: 'rgba(139, 92, 246, 0.6)',
                  boxShadow: '0 30px 80px rgba(139, 92, 246, 0.3)',
                }}
                transition={{ duration: 0.4 }}
              >
                {/* Metrics Bar */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '1px',
                  background: 'rgba(214, 221, 230, 0.1)',
                  borderBottom: '2px solid rgba(139, 92, 246, 0.3)'
                }}>
                  {feature.metrics.map((metric, i) => (
                    <motion.div
                      key={i}
                      style={{
                        background: 'rgba(10, 10, 26, 0.9)',
                        padding: '24px',
                        textAlign: 'center',
                      }}
                      initial={{ opacity: 0, y: 20 }}
                      animate={isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ duration: 0.4, delay: index * 0.2 + 0.4 + i * 0.1 }}
                      whileHover={{
                        background: 'rgba(139, 92, 246, 0.1)',
                      }}
                    >
                      <p style={{
                        fontSize: '12px',
                        color: 'rgba(214, 221, 230, 0.6)',
                        marginBottom: '8px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        fontWeight: 600
                      }}>
                        {metric.label}
                      </p>
                      <p style={{
                        fontSize: '28px',
                        fontWeight: 800,
                        color: metric.color,
                        letterSpacing: '-0.02em',
                        margin: 0
                      }}>
                        {metric.value}
                      </p>
                    </motion.div>
                  ))}
                </div>

                {/* Screenshot Display */}
                <motion.div
                  style={{
                    position: 'relative',
                    padding: '32px',
                    background: 'rgba(5, 5, 16, 0.5)'
                  }}
                  initial={{ opacity: 0 }}
                  animate={isInView ? { opacity: 1 } : {}}
                  transition={{ duration: 0.6, delay: index * 0.2 + 0.6 }}
                >
                  <div style={{
                    position: 'relative',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    {/* Gradient glow behind image */}
                    <div style={{
                      position: 'absolute',
                      inset: '-4px',
                      background: feature.gradient,
                      opacity: 0.3,
                      filter: 'blur(20px)',
                      zIndex: -1
                    }} />
                    
                    {/* Screenshot - replace with your own images */}
                    <Image
                      src={feature.image}
                      alt={feature.title}
                      width={1200}
                      height={800}
                      style={{
                        width: '100%',
                        height: 'auto',
                        display: 'block',
                        borderRadius: '16px'
                      }}
                      priority={index === 0}
                    />
                    
                    {/* Shine effect overlay */}
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: '-100%',
                      width: '100%',
                      height: '100%',
                      background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent)',
                      animation: 'shine 4s infinite',
                      pointerEvents: 'none'
                    }} />
                  </div>

                  {/* CTA Button */}
                  <Link href="/signup" style={{ textDecoration: 'none' }}>
                    <motion.div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '14px 28px',
                        borderRadius: '12px',
                        background: feature.gradient,
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '16px',
                        cursor: 'pointer',
                        marginTop: '24px',
                        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)'
                      }}
                      whileHover={{ scale: 1.05, boxShadow: '0 12px 32px rgba(139, 92, 246, 0.4)' }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Try {feature.title}
                      <ArrowRight size={20} />
                    </motion.div>
                  </Link>
                </motion.div>
              </motion.div>
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

  const steps = [
    {
      number: '1',
      title: 'Connect Your Apps',
      description: 'Link your favorite tools with one-click OAuth. No API keys needed.',
    },
    {
      number: '2',
      title: 'Build Your Workflow',
      description: 'Use the visual editor or describe in plain English. AI helps you every step.',
    },
    {
      number: '3',
      title: 'Activate & Relax',
      description: 'Your automation runs 24/7. Get notified when actions need approval.',
    },
  ];

  return (
    <div id="how-it-works" style={{ background: 'transparent', padding: '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 48px' }}>
        <motion.div
          ref={ref}
          style={{ textAlign: 'center', marginBottom: 64 }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16, color: styles.textPrimary }}>
            Up and Running in Minutes
          </h2>
          <p style={{ fontSize: 20, color: styles.textSecondary }}>
            From zero to automated in three simple steps
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 32, marginBottom: 48 }}>
          {steps.map((step, index) => (
            <motion.div
              key={index}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                borderRadius: 16,
                border: '1.5px solid rgba(255, 255, 255, 0.2)',
                padding: 32,
                position: 'relative',
                overflow: 'hidden',
              }}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              whileHover={{
                scale: 1.05,
                borderColor: 'rgba(139, 92, 246, 0.6)',
                boxShadow: '0 20px 50px rgba(139, 92, 246, 0.3)',
              }}
            >
              <div style={{
                position: 'absolute',
                top: 0,
                right: 0,
                fontSize: 120,
                lineHeight: 1,
                color: 'rgba(139, 92, 246, 0.08)',
                fontWeight: 800,
              }}>
                {step.number}
              </div>
              <div style={{ position: 'relative', zIndex: 10 }}>
                <div style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 16,
                  boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
                }}>
                  <span style={{ color: '#ffffff', fontSize: 24, fontWeight: 700 }}>
                    {step.number}
                  </span>
                </div>
                <h3 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>
                  {step.title}
                </h3>
                <p style={{ fontSize: 16, color: styles.textSecondary, margin: 0 }}>
                  {step.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function IntegrationsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const integrations = [
    { name: 'Google', icon: '📧' },
    { name: 'Slack', icon: '💬' },
    { name: 'Stripe', icon: '💳' },
    { name: 'Notion', icon: '📝' },
    { name: 'Calendly', icon: '📅' },
    { name: 'Airtable', icon: '📊' },
    { name: 'Mailchimp', icon: '✉️' },
    { name: 'Twilio', icon: '📱' },
    { name: 'GitHub', icon: '🐙' },
    { name: 'Shopify', icon: '🛒' },
    { name: 'HubSpot', icon: '🎯' },
    { name: 'Salesforce', icon: '☁️' },
  ];

  return (
    <div id="integrations" style={{ background: 'transparent', padding: '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 48px' }}>
        <motion.div
          ref={ref}
          style={{ textAlign: 'center', marginBottom: 64 }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
        >
          <h2 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16, color: styles.textPrimary }}>
            Connect Your Favorite Apps
          </h2>
          <p style={{ fontSize: 20, color: styles.textSecondary }}>
            50+ integrations and growing. One-click OAuth connection.
          </p>
        </motion.div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, justifyContent: 'center' }}>
          {integrations.map((integration, i) => (
            <motion.div
              key={i}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              style={{
                background: hoveredIndex === i 
                  ? 'rgba(139, 92, 246, 0.15)' 
                  : 'rgba(214,221,230,0.05)',
                border: hoveredIndex === i 
                  ? '1.5px solid #8b5cf6' 
                  : '1.5px solid rgba(214,221,230,0.2)',
                borderRadius: 16,
                padding: '18px 24px',
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                minWidth: 160,
                cursor: 'pointer',
                boxShadow: hoveredIndex === i 
                  ? '0 10px 30px rgba(139, 92, 246, 0.3)' 
                  : 'none',
                transform: hoveredIndex === i ? 'scale(1.05)' : 'scale(1)',
                transition: 'all 0.2s ease-out',
              }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={isInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.5, delay: i * 0.05 }}
            >
              <span style={{ fontSize: 28 }}>{integration.icon}</span>
              <span style={{ fontSize: 16, fontWeight: 600, color: styles.textPrimary }}>
                {integration.name}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PricingSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const plans = [
    { name: 'Starter', price: 'Free', description: 'For individuals getting started', features: ['5 active workflows', '1,000 executions/mo', 'Core integrations', 'Email support'] },
    { name: 'Pro', price: '$29', description: 'For growing teams', features: ['Unlimited workflows', '50,000 executions/mo', 'All integrations', 'Priority support', 'Team collaboration'], popular: true },
    { name: 'Enterprise', price: 'Custom', description: 'For large organizations', features: ['Everything in Pro', 'Unlimited executions', 'Custom integrations', 'Dedicated support', 'SLA guarantees', 'SSO & audit logs'] }
  ];

  return (
    <div id="pricing" style={{ background: 'transparent', padding: '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 48px' }}>
        <motion.div
          ref={ref}
          style={{ textAlign: 'center', marginBottom: 64 }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
        >
          <h2 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16, color: styles.textPrimary }}>Simple, Transparent Pricing</h2>
          <p style={{ fontSize: 20, color: styles.textSecondary }}>Start free, scale as you grow</p>
        </motion.div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 32 }}>
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(10, 10, 26, 0.6)',
                backdropFilter: 'blur(16px)',
                border: plan.popular ? `2px solid ${styles.primary}` : '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: 24,
                padding: 40,
                position: 'relative',
                boxShadow: plan.popular ? '0 0 40px rgba(139, 92, 246, 0.4)' : 'none'
              }}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              whileHover={{
                y: -10,
                borderColor: plan.popular ? styles.primary : 'rgba(139, 92, 246, 0.5)',
                boxShadow: plan.popular ? '0 10px 60px rgba(139, 92, 246, 0.5)' : '0 10px 40px rgba(139, 92, 246, 0.3)'
              }}
            >
              {plan.popular && (
                <div style={{
                  position: 'absolute',
                  top: -12,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: styles.primary,
                  color: '#ffffff',
                  padding: '4px 16px',
                  borderRadius: 999,
                  fontSize: 12,
                  fontWeight: 700
                }}>Most Popular</div>
              )}
              <h3 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>{plan.name}</h3>
              <p style={{ fontSize: 14, color: styles.textSecondary, marginBottom: 24 }}>{plan.description}</p>
              <div style={{ marginBottom: 32 }}>
                <span style={{ fontSize: 48, fontWeight: 800, color: styles.textPrimary }}>{plan.price}</span>
                {plan.price !== 'Custom' && plan.price !== 'Free' && <span style={{ fontSize: 16, color: styles.textMuted }}>/month</span>}
              </div>
              <ul style={{ listStyle: 'none', padding: 0, marginBottom: 32 }}>
                {plan.features.map((feature, j) => (
                  <li key={j} style={{ display: 'flex', alignItems: 'start', gap: 12, marginBottom: 12 }}>
                    <Check size={20} style={{ color: styles.primary, marginTop: 2 }} />
                    <span style={{ fontSize: 15, color: styles.textSecondary }}>{feature}</span>
                  </li>
                ))}
              </ul>
              <Link href="/signup" style={{ textDecoration: 'none' }}>
                <motion.div
                  style={{
                    width: '100%',
                    background: plan.popular ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : 'transparent',
                    color: plan.popular ? '#ffffff' : styles.primary,
                    padding: '16px 32px',
                    borderRadius: 8,
                    fontSize: 18,
                    fontWeight: 600,
                    border: plan.popular ? 'none' : `2px solid ${styles.primary}`,
                    cursor: 'pointer',
                    boxShadow: plan.popular ? '0 4px 20px rgba(139, 92, 246, 0.4)' : 'none',
                    textAlign: 'center'
                  }}
                  whileHover={{
                    scale: 1.02,
                    background: plan.popular ? 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)' : 'rgba(139, 92, 246, 0.1)',
                    boxShadow: plan.popular ? '0 6px 30px rgba(139, 92, 246, 0.6)' : '0 4px 20px rgba(139, 92, 246, 0.3)'
                  }}
                  whileTap={{ scale: 0.98 }}
                >
                  {plan.price === 'Custom' ? 'Contact Sales' : 'Get Started'}
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

  return (
    <div style={{ background: 'transparent', padding: '96px 0', borderTop: '1.5px solid rgba(255, 255, 255, 0.1)' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 48px' }}>
        <motion.div
          ref={ref}
          style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.1))',
            borderRadius: 24,
            border: '2px solid rgba(139, 92, 246, 0.5)',
            padding: 64,
            textAlign: 'center',
            boxShadow: '0 20px 60px rgba(139, 92, 246, 0.2)',
          }}
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
        >
          <h2 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16, color: styles.textPrimary }}>
            Ready to Automate Your Business?
          </h2>
          <p style={{ fontSize: 20, color: styles.textSecondary, marginBottom: 40, maxWidth: 600, margin: '0 auto 40px' }}>
            Join thousands of teams saving 40+ hours every month with Aivaro
          </p>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', justifyContent: 'center' }}>
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: '#ffffff',
                  padding: '16px 32px',
                  borderRadius: 8,
                  fontSize: 18,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
                }}
                whileHover={{ scale: 1.05, boxShadow: '0 6px 40px rgba(139, 92, 246, 0.6)' }}
                whileTap={{ scale: 0.95 }}
              >
                Start Building Free
                <ArrowRight size={20} />
              </motion.div>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function Footer() {
  return (
    <div style={{ background: 'transparent', padding: '80px 0 64px', borderTop: '1px solid rgba(139, 92, 246, 0.2)' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 48px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 64, marginBottom: 64 }}>
          <div>
            <div style={{ marginBottom: 16 }}>
              <Logo />
            </div>
            <p style={{ fontSize: 15, color: styles.textSecondary, lineHeight: 1.6, margin: 0 }}>
              AI-powered workflow automation for modern businesses. Build, automate, and scale without code.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <p style={{ fontSize: 16, color: styles.textPrimary, marginBottom: 8, fontWeight: 600 }}>Product</p>
            {['Features', 'Integrations', 'Templates', 'Pricing'].map((item) => (
              <motion.p
                key={item}
                style={{ fontSize: 15, color: styles.textSecondary, cursor: 'pointer', margin: 0 }}
                whileHover={{ color: '#8b5cf6', x: 5 }}
                transition={{ duration: 0.2 }}
              >
                {item}
              </motion.p>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <p style={{ fontSize: 16, color: styles.textPrimary, marginBottom: 8, fontWeight: 600 }}>Company</p>
            {['About', 'Blog', 'Careers', 'Contact'].map((item) => (
              <motion.p
                key={item}
                style={{ fontSize: 15, color: styles.textSecondary, cursor: 'pointer', margin: 0 }}
                whileHover={{ color: '#8b5cf6', x: 5 }}
                transition={{ duration: 0.2 }}
              >
                {item}
              </motion.p>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <p style={{ fontSize: 16, color: styles.textPrimary, marginBottom: 8, fontWeight: 600 }}>Legal</p>
            {['Privacy', 'Terms', 'Security'].map((item) => (
              <motion.p
                key={item}
                style={{ fontSize: 15, color: styles.textSecondary, cursor: 'pointer', margin: 0 }}
                whileHover={{ color: '#8b5cf6', x: 5 }}
                transition={{ duration: 0.2 }}
              >
                {item}
              </motion.p>
            ))}
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: 32,
          borderTop: '1.5px solid rgba(255, 255, 255, 0.1)',
        }}>
          <p style={{ fontSize: 14, color: styles.textMuted, margin: 0 }}>
            © 2026 Aivaro. All rights reserved.
          </p>
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
        @keyframes shine {
          0% { left: -100%; }
          100% { left: 200%; }
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
      {/* Fixed Background Layer */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom right, #0a0a1a 0%, #050510 50%, #020306 100%)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(139, 92, 246, 0.15), transparent 50%)' }} />
        <div style={{ position: 'absolute', top: '-10%', left: '20%', width: '800px', height: '800px', background: 'radial-gradient(circle, #8b5cf6 0%, transparent 70%)', filter: 'blur(120px)', opacity: 0.25 }} />
        <div style={{ position: 'absolute', top: '30%', right: '-5%', width: '600px', height: '600px', background: 'radial-gradient(circle, #3b82f6 0%, transparent 70%)', filter: 'blur(100px)', opacity: 0.2 }} />
        <div style={{ position: 'absolute', bottom: '10%', left: '-5%', width: '700px', height: '700px', background: 'radial-gradient(circle, #10b981 0%, transparent 70%)', filter: 'blur(110px)', opacity: 0.15 }} />
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(139, 92, 246, 0.05) 1px, transparent 0)', backgroundSize: '40px 40px' }} />
      </div>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        <Header />
        <div>
          <HeroSection />
          <StatsSection />
          <FeaturesSection />
          <FeatureShowcaseSection />
          <HowItWorksSection />
          <IntegrationsSection />
          <PricingSection />
          <CTASection />
          <Footer />
        </div>
      </div>
    </div>
  );
}

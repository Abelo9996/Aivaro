'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect, useRef } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Zap, Shield, TrendingUp, Clock, Check, Bot, Workflow, Globe, Sparkles, Play, GitBranch, Users, Menu, X } from 'lucide-react';

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

// Responsive breakpoints hook
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

function Logo({ small = false }: { small?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <img 
        src="/logo.png" 
        alt="Aivaro" 
        style={{ height: small ? 32 : 40, width: 'auto' }}
      />
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
        <div style={{ 
          maxWidth: 1440, 
          margin: '0 auto', 
          padding: isMobile ? '8px 16px' : (scrolled ? '8px 48px' : '8px 48px'),
          transition: 'all 500ms'
        }}>
          <div style={{
            backdropFilter: scrolled ? 'none' : (isMobile ? 'none' : 'blur(48px)'),
            background: scrolled ? 'transparent' : (isMobile ? 'transparent' : 'rgba(139, 92, 246, 0.08)'),
            display: 'flex',
            gap: isMobile ? 0 : 96,
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: isMobile ? '8px 0' : '8px 24px',
            borderRadius: scrolled ? 0 : 16,
            boxShadow: scrolled || isMobile ? 'none' : '0px 4px 24px rgba(0, 0, 0, 0.16)',
            transition: 'all 500ms'
          }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                transition={{ duration: 0.2 }}
              >
                <Logo small={isMobile} />
              </motion.div>
            </Link>
            
            {/* Desktop Navigation */}
            {!isMobile && !isTablet && (
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
                <Link href="/demo" style={{ textDecoration: 'none' }}>
                  <motion.span 
                    style={{
                      color: styles.primary,
                      fontSize: 15,
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4
                    }}
                    whileHover={{ 
                      scale: 1.05
                    }}
                    transition={{ duration: 0.2 }}
                  >
                    <Play size={14} />
                    Demo
                  </motion.span>
                </Link>
              </div>
            )}
            
            {/* Desktop Buttons */}
            {!isMobile && (
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
                    Get Started
                  </motion.div>
                </Link>
              </div>
            )}
            
            {/* Mobile Menu Button */}
            {isMobile && (
              <motion.button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: styles.textPrimary,
                  cursor: 'pointer',
                  padding: 8,
                }}
                whileTap={{ scale: 0.95 }}
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>
      
      {/* Mobile Menu Dropdown */}
      {isMobile && mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          style={{
            position: 'fixed',
            top: 60,
            left: 0,
            right: 0,
            background: 'rgba(10, 10, 26, 0.98)',
            backdropFilter: 'blur(20px)',
            zIndex: 999,
            padding: '24px 16px',
            borderBottom: '1px solid rgba(139, 92, 246, 0.2)',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {['features', 'how-it-works', 'integrations', 'pricing'].map((item) => (
              <motion.a 
                key={item}
                href={`#${item}`}
                onClick={(e) => {
                  e.preventDefault();
                  smoothScrollTo(item);
                  setMobileMenuOpen(false);
                }}
                style={{
                  color: styles.textPrimary,
                  fontSize: 18,
                  fontWeight: 500,
                  textDecoration: 'none',
                  padding: '12px 0',
                  borderBottom: '1px solid rgba(255,255,255,0.1)',
                  textTransform: 'capitalize'
                }}
              >
                {item.replace('-', ' ')}
              </motion.a>
            ))}
            <Link 
              href="/demo" 
              style={{ textDecoration: 'none' }}
              onClick={() => setMobileMenuOpen(false)}
            >
              <div
                style={{
                  color: styles.primary,
                  fontSize: 18,
                  fontWeight: 600,
                  padding: '12px 0',
                  borderBottom: '1px solid rgba(255,255,255,0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}
              >
                <Play size={18} />
                Watch Demo
              </div>
            </Link>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 16 }}>
              <Link href="/login" style={{ textDecoration: 'none' }}>
                <div
                  style={{
                    background: 'transparent',
                    color: styles.textPrimary,
                    padding: '14px 24px',
                    borderRadius: 8,
                    fontSize: 16,
                    border: '1.5px solid rgba(139, 92, 246, 0.3)',
                    textAlign: 'center',
                  }}
                >
                  Sign in
                </div>
              </Link>
              <Link href="/signup" style={{ textDecoration: 'none' }}>
                <div
                  style={{
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                    color: '#ffffff',
                    padding: '14px 24px',
                    borderRadius: 8,
                    fontSize: 16,
                    fontWeight: 600,
                    textAlign: 'center',
                  }}
                >
                  Get Started Free
                </div>
              </Link>
            </div>
          </div>
        </motion.div>
      )}
    </>
  );
}

function HeroSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '15%']);
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0.3]);
  const { isMobile, isTablet } = useResponsive();

  return (
    <div ref={ref} style={{ background: 'transparent', position: 'relative', overflow: 'hidden' }}>
      <div style={{ 
        maxWidth: 1440, 
        margin: '0 auto', 
        padding: isMobile ? '48px 16px' : isTablet ? '64px 32px' : '96px 96px' 
      }}>
        <motion.div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 32 : 48, alignItems: 'center', y, opacity }}>
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
            <span style={{ fontSize: isMobile ? 12 : 14, color: styles.primary, fontWeight: 600 }}>✨ Your Personalized AI Co-Founder</span>
          </motion.div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 16 : 24, alignItems: 'center', maxWidth: 900 }}>
            <motion.h1
              style={{
                fontSize: isMobile ? 36 : isTablet ? 48 : 72,
                lineHeight: 1.1,
                letterSpacing: isMobile ? '-1px' : '-2px',
                fontWeight: 800,
                color: styles.textPrimary,
                textAlign: 'center',
                margin: 0
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Tell Us What You Need.{' '}
              <span style={{ 
                background: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                We Execute.
              </span>
            </motion.h1>
            <motion.p
              style={{
                fontSize: isMobile ? 16 : isTablet ? 20 : 24,
                lineHeight: isMobile ? '24px' : '32px',
                color: styles.textPrimary,
                opacity: 0.8,
                textAlign: 'center',
                margin: 0,
                padding: isMobile ? '0 8px' : 0
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              Describe your business workflow in plain English. Aivaro builds and runs it automatically. Not suggestions. Not drafts. Execution.
            </motion.p>
          </div>

          <motion.div
            style={{ 
              display: 'flex', 
              flexDirection: isMobile ? 'column' : 'row',
              gap: 16, 
              alignItems: 'center',
              width: isMobile ? '100%' : 'auto'
            }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Link href="/signup" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: '#ffffff',
                  padding: isMobile ? '14px 24px' : '16px 32px',
                  borderRadius: 8,
                  fontSize: isMobile ? 16 : 18,
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
                  width: isMobile ? '100%' : 'auto'
                }}
                whileHover={{ scale: 1.05, boxShadow: '0 6px 30px rgba(139, 92, 246, 0.6)' }}
                whileTap={{ scale: 0.95 }}
              >
                Start Building Free
                <ArrowRight size={20} />
              </motion.div>
            </Link>
            <Link href="/demo" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{
                  background: 'transparent',
                  color: styles.primary,
                  padding: isMobile ? '14px 24px' : '16px 32px',
                  borderRadius: 8,
                  fontSize: isMobile ? 16 : 18,
                  fontWeight: 600,
                  border: `2px solid ${styles.primary}`,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  width: '100%'
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
            </Link>
          </motion.div>

          <motion.p
            style={{ fontSize: isMobile ? 13 : 15, color: styles.textMuted, textAlign: 'center', margin: 0 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            No credit card required • Setup in 2 minutes • Cancel anytime
          </motion.p>

          {/* Dashboard Preview */}
          <motion.div
            style={{ width: '100%', maxWidth: 1100, marginTop: isMobile ? 32 : 64 }}
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <motion.div
              style={{
                background: 'linear-gradient(135deg, rgba(30, 30, 40, 0.95) 0%, rgba(20, 20, 35, 0.95) 100%)',
                borderRadius: isMobile ? 12 : 20,
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
                padding: isMobile ? '8px 12px' : '12px 20px',
                borderBottom: '1px solid rgba(139, 92, 246, 0.2)',
                display: 'flex',
                alignItems: 'center',
                gap: isMobile ? 8 : 12
              }}>
                <div style={{ display: 'flex', gap: isMobile ? 6 : 8 }}>
                  <div style={{ width: isMobile ? 10 : 12, height: isMobile ? 10 : 12, borderRadius: '50%', background: '#ff5f56' }} />
                  <div style={{ width: isMobile ? 10 : 12, height: isMobile ? 10 : 12, borderRadius: '50%', background: '#ffbd2e' }} />
                  <div style={{ width: isMobile ? 10 : 12, height: isMobile ? 10 : 12, borderRadius: '50%', background: '#27c93f' }} />
                </div>
                <div style={{ 
                  flex: 1,
                  background: 'rgba(10, 10, 26, 0.6)',
                  borderRadius: 8,
                  padding: isMobile ? '4px 10px' : '6px 16px',
                  fontSize: isMobile ? 11 : 13,
                  color: styles.textMuted,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}>
                  <Shield size={isMobile ? 12 : 14} color={styles.primary} />
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>app.aivaro.io/workflows</span>
                </div>
              </div>

              {/* Workflow Editor Preview */}
              <div style={{ padding: isMobile ? '24px 16px' : '48px 40px' }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: isMobile ? 20 : 36 }}>
                  <Logo />
                  <span style={{ color: styles.textMuted, marginLeft: isMobile ? 8 : 16, fontSize: isMobile ? 12 : 14 }}>Workflow Editor</span>
                </div>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', 
                  gap: isMobile ? 12 : 20 
                }}>
                  {[
                    { label: 'Active Workflows', value: '24', icon: <Workflow size={isMobile ? 16 : 20} /> },
                    { label: 'Time Saved Weekly', value: '38h', icon: <Clock size={isMobile ? 16 : 20} /> },
                    { label: 'Tasks Automated', value: '2.4K', icon: <Zap size={isMobile ? 16 : 20} /> }
                  ].map((stat, i) => (
                    <motion.div
                      key={i}
                      style={{ 
                        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)',
                        padding: isMobile ? '16px' : '28px 24px', 
                        borderRadius: isMobile ? 12 : 16,
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
                        top: isMobile ? 12 : 16,
                        right: isMobile ? 12 : 16,
                        color: styles.primary,
                        opacity: 0.5
                      }}>
                        {stat.icon}
                      </div>
                      
                      <p style={{ 
                        color: styles.textSecondary, 
                        fontSize: isMobile ? 11 : 13, 
                        marginBottom: isMobile ? 4 : 8, 
                        margin: 0,
                        fontWeight: 500,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}>
                        {stat.label}
                      </p>
                      <p style={{ 
                        color: styles.textPrimary, 
                        fontSize: isMobile ? 24 : 36, 
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
  const { isMobile, isTablet } = useResponsive();
  const stats = [
    { icon: <TrendingUp size={isMobile ? 24 : 32} />, value: '10x', label: 'Faster than manual' },
    { icon: <Clock size={isMobile ? 24 : 32} />, value: '5+hrs', label: 'Saved weekly' },
    { icon: <Shield size={isMobile ? 24 : 32} />, value: '100%', label: 'Human approval' },
    { icon: <Zap size={isMobile ? 24 : 32} />, value: '24/7', label: 'Always running' }
  ];

  return (
    <div style={{ background: 'transparent', padding: isMobile ? '48px 0' : '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: isMobile ? '0 16px' : '0 48px' }}>
        <motion.div ref={ref} style={{ 
          display: 'grid', 
          gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : isTablet ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', 
          gap: isMobile ? 12 : 32 
        }}>
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(10, 10, 26, 0.6)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: isMobile ? 12 : 20,
                padding: isMobile ? 16 : 32,
                textAlign: 'center'
              }}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: i * 0.1 }}
            >
              <div style={{ color: styles.primary, marginBottom: isMobile ? 8 : 16 }}>{stat.icon}</div>
              <div style={{ color: styles.textPrimary, fontSize: isMobile ? 28 : 48, fontWeight: 800, marginBottom: isMobile ? 4 : 8 }}>{stat.value}</div>
              <div style={{ color: styles.textSecondary, fontSize: isMobile ? 12 : 16 }}>{stat.label}</div>
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
  const { isMobile, isTablet } = useResponsive();

  const features = [
    {
      icon: <Bot size={isMobile ? 24 : 32} />,
      title: 'Plain-English to Workflow',
      description: 'Describe what you need in plain English, and Aivaro builds the entire workflow for you. No coding or technical knowledge required.',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    },
    {
      icon: <Zap size={isMobile ? 24 : 32} />,
      title: 'Email-Triggered Automation',
      description: 'Workflows trigger automatically when matching emails arrive. Extract data, create calendar events, send payment links — all hands-free.',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    },
    {
      icon: <Globe size={isMobile ? 24 : 32} />,
      title: 'Google & Stripe Integration',
      description: 'Connect Gmail, Google Sheets, Google Calendar, and Stripe with one-click OAuth. Your data flows seamlessly between tools.',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
    {
      icon: <Users size={isMobile ? 24 : 32} />,
      title: 'Approval Guardrails',
      description: 'Mark sensitive actions to require your approval before executing. Get notified and approve or reject with a single click.',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
      icon: <TrendingUp size={isMobile ? 24 : 32} />,
      title: 'AI Data Extraction',
      description: 'AI automatically extracts customer names, dates, times, and details from emails. No regex, no parsing — just intelligent extraction.',
      gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
    },
    {
      icon: <Sparkles size={isMobile ? 24 : 32} />,
      title: 'Execution History & Logs',
      description: 'See every workflow run, every step executed, every result. Full transparency with detailed logs and output data.',
      gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
    },
  ];

  return (
    <div id="features" ref={ref} style={{ 
      padding: isMobile ? '60px 0' : '120px 0', 
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

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: isMobile ? '0 16px' : '0 24px', position: 'relative', zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          style={{ textAlign: 'center', marginBottom: isMobile ? 40 : 80 }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            style={{
              display: 'inline-block',
              padding: isMobile ? '8px 16px' : '10px 24px',
              borderRadius: 999,
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1.5px solid rgba(139, 92, 246, 0.3)',
              marginBottom: isMobile ? 16 : 24,
            }}
          >
            <span style={{ color: styles.primary, fontSize: isMobile ? 12 : 14, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              ⚡ Powerful Features
            </span>
          </motion.div>
          <h2 style={{ fontSize: isMobile ? 32 : isTablet ? 44 : 56, fontWeight: 800, color: styles.textPrimary, marginBottom: isMobile ? 12 : 20, lineHeight: 1.1 }}>
            Everything You Need to Execute
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 20, color: styles.textSecondary, maxWidth: 800, margin: '0 auto', lineHeight: 1.7, padding: isMobile ? '0 8px' : 0 }}>
            Revenue loops that run without babysitting. Built for founders, not engineers.
          </p>
        </motion.div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)', 
          gap: isMobile ? 16 : 24 
        }}>
          {features.map((feature, index) => (
            <motion.div
              key={index}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                borderRadius: isMobile ? 12 : 16,
                border: '1.5px solid rgba(255, 255, 255, 0.2)',
                padding: isMobile ? 20 : 32,
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
                  width: isMobile ? 44 : 56,
                  height: isMobile ? 44 : 56,
                  borderRadius: isMobile ? 10 : 12,
                  background: feature.gradient,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  marginBottom: isMobile ? 16 : 24,
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)'
                }}
              >
                {feature.icon}
              </div>
              <h3 style={{ fontSize: isMobile ? 18 : 20, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>
                {feature.title}
              </h3>
              <p style={{ fontSize: isMobile ? 14 : 16, color: styles.textSecondary, margin: 0, lineHeight: 1.6 }}>
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
  const { isMobile, isTablet } = useResponsive();

  const features = [
    {
      id: 1,
      title: 'Visual Workflow Builder',
      description: 'Drag and drop to create powerful automations. Connect triggers, actions, and logic nodes in an intuitive canvas editor.',
      image: '/images/example_tool_1.png',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
      metrics: [
        { label: 'Node Types', value: '15+', color: '#8b5cf6' },
        { label: 'Setup Time', value: '< 5min', color: '#7c3aed' },
        { label: 'No Code', value: '100%', color: '#10b981' },
      ]
    },
    {
      id: 2,
      title: 'AI-Powered Generation',
      description: 'Describe what you want in plain English. AI builds the entire workflow — triggers, actions, and connections — automatically.',
      image: '/images/example_tool_2.png',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
      metrics: [
        { label: 'Generation', value: '< 5s', color: '#3b82f6' },
        { label: 'Data Extract', value: 'AI', color: '#2563eb' },
        { label: 'Timezone', value: 'Pacific', color: '#10b981' },
      ]
    },
    {
      id: 3,
      title: 'Pre-Built Workflow Templates',
      description: 'Get started instantly with ready-to-use workflow templates. From booking confirmations to invoice processing — just customize and deploy.',
      image: '/images/example_tool_3.png',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      metrics: [
        { label: 'Templates', value: '10+', color: '#10b981' },
        { label: 'Setup', value: '< 2min', color: '#059669' },
        { label: 'Customizable', value: '100%', color: '#10b981' },
      ]
    },
    {
      id: 4,
      title: 'One-Click Integrations',
      description: 'Connect Google (Gmail, Sheets, Calendar) and Stripe with secure OAuth. No API keys to manage — just authorize and go.',
      image: '/images/example_tool_4.png',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      metrics: [
        { label: 'Integrations', value: '4', color: '#f59e0b' },
        { label: 'Setup', value: '< 30s', color: '#d97706' },
        { label: 'Security', value: 'OAuth 2', color: '#10b981' },
      ]
    }
  ];

  return (
    <div id="showcase" ref={ref} style={{ 
      padding: isMobile ? '60px 0' : '120px 0', 
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

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: isMobile ? '0 16px' : '0 24px', position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          style={{ textAlign: 'center', marginBottom: isMobile ? '40px' : '80px' }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            style={{
              display: 'inline-block',
              padding: isMobile ? '8px 16px' : '10px 24px',
              borderRadius: 999,
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1.5px solid rgba(139, 92, 246, 0.3)',
              marginBottom: isMobile ? '16px' : '24px',
              boxShadow: '0 4px 16px rgba(139, 92, 246, 0.2)'
            }}
          >
            <span style={{ 
              color: styles.primary, 
              fontSize: isMobile ? '12px' : '14px', 
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase'
            }}>
              🎬 Product Tour
            </span>
          </motion.div>
          <h2 style={{
            fontSize: isMobile ? '32px' : isTablet ? '44px' : '56px',
            fontWeight: 800,
            color: styles.textPrimary,
            marginBottom: isMobile ? '12px' : '20px',
            lineHeight: 1.1,
            letterSpacing: '-0.02em'
          }}>
            See Aivaro in Action
          </h2>
          <p style={{
            fontSize: isMobile ? '16px' : '20px',
            color: styles.textSecondary,
            maxWidth: '800px',
            margin: '0 auto',
            lineHeight: 1.7,
            padding: isMobile ? '0 8px' : 0
          }}>
            Watch how our visual workflow builder turns complex automations into simple drag-and-drop experiences
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? '60px' : '120px' }}>
          {features.map((feature, index) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 80 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: index * 0.2 }}
            >
              {/* Title and Description */}
              <div style={{ marginBottom: isMobile ? '20px' : '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? '12px' : '16px', marginBottom: isMobile ? '12px' : '16px' }}>
                  <div style={{
                    display: 'flex',
                    width: isMobile ? '36px' : '48px',
                    height: isMobile ? '36px' : '48px',
                    borderRadius: isMobile ? '10px' : '12px',
                    background: feature.gradient,
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: isMobile ? '18px' : '22px',
                    fontWeight: 700,
                    color: 'white',
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)'
                  }}>
                    {feature.id}
                  </div>
                  <h3 style={{
                    fontSize: isMobile ? '22px' : isTablet ? '28px' : '36px',
                    fontWeight: 700,
                    color: styles.textPrimary,
                    lineHeight: 1.2,
                    letterSpacing: '-0.02em'
                  }}>
                    {feature.title}
                  </h3>
                </div>
                <p style={{
                  fontSize: isMobile ? '14px' : '18px',
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
                  borderRadius: isMobile ? '16px' : '24px',
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
                        padding: isMobile ? '16px 12px' : '24px',
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
                        fontSize: isMobile ? '10px' : '12px',
                        color: 'rgba(214, 221, 230, 0.6)',
                        marginBottom: isMobile ? '4px' : '8px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        fontWeight: 600
                      }}>
                        {metric.label}
                      </p>
                      <p style={{
                        fontSize: isMobile ? '20px' : '28px',
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
                    padding: isMobile ? '16px' : '32px',
                    background: 'rgba(5, 5, 16, 0.5)'
                  }}
                  initial={{ opacity: 0 }}
                  animate={isInView ? { opacity: 1 } : {}}
                  transition={{ duration: 0.6, delay: index * 0.2 + 0.6 }}
                >
                  <div style={{
                    position: 'relative',
                    borderRadius: isMobile ? '12px' : '16px',
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
                        padding: isMobile ? '12px 20px' : '14px 28px',
                        borderRadius: '12px',
                        background: feature.gradient,
                        color: 'white',
                        fontWeight: 600,
                        fontSize: isMobile ? '14px' : '16px',
                        cursor: 'pointer',
                        marginTop: isMobile ? '16px' : '24px',
                        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)'
                      }}
                      whileHover={{ scale: 1.05, boxShadow: '0 12px 32px rgba(139, 92, 246, 0.4)' }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Try {feature.title}
                      <ArrowRight size={isMobile ? 16 : 20} />
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
  const { isMobile, isTablet } = useResponsive();

  const steps = [
    {
      number: '1',
      title: 'Connect Your Accounts',
      description: 'Link Google (Gmail, Sheets, Calendar) and Stripe with secure one-click OAuth.',
    },
    {
      number: '2',
      title: 'Describe or Build',
      description: 'Tell AI what you need in plain English, or use the visual editor to craft your workflow.',
    },
    {
      number: '3',
      title: 'Activate & Monitor',
      description: 'Your workflow runs automatically on triggers. Review executions and approve sensitive actions.',
    },
  ];

  return (
    <div id="how-it-works" style={{ background: 'transparent', padding: isMobile ? '48px 0' : '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: isMobile ? '0 16px' : '0 48px' }}>
        <motion.div
          ref={ref}
          style={{ textAlign: 'center', marginBottom: isMobile ? 32 : 64 }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 style={{ fontSize: isMobile ? 32 : 48, fontWeight: 800, marginBottom: isMobile ? 12 : 16, color: styles.textPrimary }}>
            Up and Running in Minutes
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 20, color: styles.textSecondary }}>
            From zero to automated in three simple steps
          </p>
        </motion.div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)', 
          gap: isMobile ? 16 : 32, 
          marginBottom: isMobile ? 24 : 48 
        }}>
          {steps.map((step, index) => (
            <motion.div
              key={index}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                borderRadius: isMobile ? 12 : 16,
                border: '1.5px solid rgba(255, 255, 255, 0.2)',
                padding: isMobile ? 20 : 32,
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
                fontSize: isMobile ? 80 : 120,
                lineHeight: 1,
                color: 'rgba(139, 92, 246, 0.08)',
                fontWeight: 800,
              }}>
                {step.number}
              </div>
              <div style={{ position: 'relative', zIndex: 10 }}>
                <div style={{
                  width: isMobile ? 40 : 48,
                  height: isMobile ? 40 : 48,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: isMobile ? 12 : 16,
                  boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
                }}>
                  <span style={{ color: '#ffffff', fontSize: isMobile ? 20 : 24, fontWeight: 700 }}>
                    {step.number}
                  </span>
                </div>
                <h3 style={{ fontSize: isMobile ? 20 : 24, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>
                  {step.title}
                </h3>
                <p style={{ fontSize: isMobile ? 14 : 16, color: styles.textSecondary, margin: 0 }}>
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
  const [activeCategory, setActiveCategory] = useState('all');
  const { isMobile, isTablet } = useResponsive();

  const categories = [
    { id: 'all', name: 'All Tools', count: 37 },
    { id: 'core', name: 'Core', count: 4 },
    { id: 'crm', name: 'CRM & Sales', count: 4 },
    { id: 'productivity', name: 'Productivity', count: 6 },
    { id: 'marketing', name: 'Marketing', count: 4 },
    { id: 'analytics', name: 'Analytics', count: 4 },
    { id: 'webdev', name: 'Web Dev', count: 6 },
    { id: 'social', name: 'Social Media', count: 5 },
    { id: 'support', name: 'Support', count: 4 },
  ];

  const allIntegrations = [
    // Core
    { name: 'Gmail', icon: '/icons/gmail.svg', category: 'core' },
    { name: 'Google Sheets', icon: '/icons/sheets.svg', category: 'core' },
    { name: 'Google Calendar', icon: '/icons/calendar.svg', category: 'core' },
    { name: 'Stripe', icon: '/icons/stripe.svg', category: 'core' },
    // CRM & Sales
    { name: 'HubSpot', icon: '/icons/hubspot.svg', category: 'crm' },
    { name: 'Salesforce', icon: '/icons/salesforce.svg', category: 'crm' },
    { name: 'Airtable', icon: '/icons/airtable.svg', category: 'crm' },
    { name: 'QuickBooks', icon: '/icons/quickbooks.svg', category: 'crm' },
    // Productivity
    { name: 'Slack', icon: '/icons/slack.svg', category: 'productivity' },
    { name: 'Notion', icon: '/icons/notion.svg', category: 'productivity' },
    { name: 'Asana', icon: '/icons/asana.svg', category: 'productivity' },
    { name: 'Trello', icon: '/icons/trello.svg', category: 'productivity' },
    { name: 'Linear', icon: '/icons/linear.svg', category: 'productivity' },
    { name: 'Jira', icon: '/icons/jira.svg', category: 'productivity' },
    // Marketing
    { name: 'Mailchimp', icon: '/icons/mailchimp.svg', category: 'marketing' },
    { name: 'Twilio', icon: '/icons/twilio.svg', category: 'marketing' },
    { name: 'Textedly', icon: '/icons/textedly.svg', category: 'marketing' },
    { name: 'Calendly', icon: '/icons/calendly.svg', category: 'marketing' },
    // Analytics & Traffic
    { name: 'Google Analytics', icon: '/icons/google-analytics.svg', category: 'analytics' },
    { name: 'Cloudflare', icon: '/icons/cloudflare.svg', category: 'analytics' },
    { name: 'Plausible', icon: '/icons/plausible.svg', category: 'analytics' },
    { name: 'Hotjar', icon: '/icons/hotjar.svg', category: 'analytics' },
    // Web Development
    { name: 'GitHub', icon: '/icons/github.svg', category: 'webdev' },
    { name: 'Webflow', icon: '/icons/webflow.svg', category: 'webdev' },
    { name: 'Wix', icon: '/icons/wix.svg', category: 'webdev' },
    { name: 'Squarespace', icon: '/icons/squarespace.svg', category: 'webdev' },
    { name: 'GoDaddy', icon: '/icons/godaddy.svg', category: 'webdev' },
    { name: 'Shopify', icon: '/icons/shopify.svg', category: 'webdev' },
    // Social Media
    { name: 'Facebook', icon: '/icons/facebook.svg', category: 'social' },
    { name: 'Instagram', icon: '/icons/instagram.svg', category: 'social' },
    { name: 'LinkedIn', icon: '/icons/linkedin.svg', category: 'social' },
    { name: 'Twitter', icon: '/icons/twitter.svg', category: 'social' },
    { name: 'TikTok', icon: '/icons/tiktok.svg', category: 'social' },
    // Support
    { name: 'Discord', icon: '/icons/discord.svg', category: 'support' },
    { name: 'Zendesk', icon: '/icons/zendesk.svg', category: 'support' },
    { name: 'Intercom', icon: '/icons/intercom.svg', category: 'support' },
    { name: 'Zapier', icon: '/icons/zapier.svg', category: 'support' },
  ];

  const filteredIntegrations = activeCategory === 'all' 
    ? allIntegrations 
    : allIntegrations.filter(i => i.category === activeCategory);

  return (
    <div id="integrations" style={{ background: 'transparent', padding: isMobile ? '48px 0' : '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: isMobile ? '0 16px' : '0 48px' }}>
        <motion.div
          ref={ref}
          style={{ textAlign: 'center', marginBottom: isMobile ? 32 : 48 }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
        >
          <h2 style={{ fontSize: isMobile ? 32 : 48, fontWeight: 800, marginBottom: isMobile ? 12 : 16, color: styles.textPrimary }}>
            37+ Powerful Integrations
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 20, color: styles.textSecondary, maxWidth: 600, margin: '0 auto' }}>
            Connect your essential business tools with one-click OAuth. From CRM to analytics, marketing to web development.
          </p>
        </motion.div>

        {/* Category Filter Tabs */}
        <motion.div 
          style={{ 
            display: 'flex', 
            flexWrap: 'wrap',
            justifyContent: 'center', 
            gap: isMobile ? 8 : 12, 
            marginBottom: isMobile ? 24 : 40 
          }}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.2 }}
        >
          {categories.map((cat) => (
            <motion.button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              style={{
                background: activeCategory === cat.id 
                  ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' 
                  : 'rgba(139, 92, 246, 0.1)',
                border: activeCategory === cat.id 
                  ? 'none' 
                  : '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: 20,
                padding: isMobile ? '8px 14px' : '10px 20px',
                color: activeCategory === cat.id ? 'white' : styles.textSecondary,
                fontSize: isMobile ? 12 : 14,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {cat.name}
            </motion.button>
          ))}
        </motion.div>

        {/* Integrations Grid */}
        <motion.div 
          style={{ 
            display: 'grid', 
            gridTemplateColumns: isMobile ? 'repeat(3, 1fr)' : isTablet ? 'repeat(4, 1fr)' : 'repeat(6, 1fr)',
            gap: isMobile ? 12 : 20, 
            justifyContent: 'center' 
          }}
          layout
        >
          {filteredIntegrations.map((integration, i) => (
            <motion.div
              key={integration.name}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              style={{
                background: hoveredIndex === i 
                  ? 'rgba(139, 92, 246, 0.15)' 
                  : 'rgba(214,221,230,0.05)',
                border: hoveredIndex === i 
                  ? '1.5px solid #8b5cf6' 
                  : '1.5px solid rgba(214,221,230,0.15)',
                borderRadius: isMobile ? 12 : 16,
                padding: isMobile ? '16px 8px' : '20px 16px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: isMobile ? 8 : 12,
                cursor: 'pointer',
                boxShadow: hoveredIndex === i 
                  ? '0 10px 30px rgba(139, 92, 246, 0.3)' 
                  : 'none',
                transition: 'all 0.2s ease-out',
              }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: hoveredIndex === i ? 1.05 : 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3, delay: i * 0.02 }}
              layout
            >
              <img 
                src={integration.icon} 
                alt={integration.name} 
                style={{ 
                  width: isMobile ? 32 : 40, 
                  height: isMobile ? 32 : 40, 
                  objectFit: 'contain' 
                }} 
              />
              <span style={{ 
                fontSize: isMobile ? 11 : 13, 
                fontWeight: 600, 
                color: styles.textPrimary, 
                textAlign: 'center',
                lineHeight: 1.2
              }}>
                {integration.name}
              </span>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          style={{ textAlign: 'center', marginTop: isMobile ? 32 : 48 }}
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          <p style={{ 
            fontSize: isMobile ? 14 : 16, 
            color: styles.textMuted, 
            marginBottom: 16 
          }}>
            Don't see your favorite tool? We're adding new integrations every week.
          </p>
          <motion.a
            href="#"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              color: styles.primary,
              fontSize: isMobile ? 14 : 16,
              fontWeight: 600,
              textDecoration: 'none',
            }}
            whileHover={{ scale: 1.05, color: styles.primaryLight }}
          >
            Request an Integration <ArrowRight size={18} />
          </motion.a>
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
    { name: 'Starter', description: 'Perfect for trying out Aivaro', features: ['Limited active workflows', 'Basic executions', 'Core integrations', 'Email triggers', 'Community support'] },
    { name: 'Pro', description: 'For growing businesses', features: ['More active workflows', 'Increased executions', 'All integrations', 'Approval workflows', 'AI data extraction', 'Priority support'], popular: true },
    { name: 'Enterprise', description: 'For scaling operations', features: ['Unlimited workflows', 'Unlimited executions', 'All integrations', 'Advanced analytics', 'Custom triggers', 'Dedicated support', 'Team collaboration'] }
  ];

  return (
    <div id="pricing" style={{ background: 'transparent', padding: isMobile ? '48px 0' : '96px 0' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: isMobile ? '0 16px' : '0 48px' }}>
        <motion.div
          ref={ref}
          style={{ textAlign: 'center', marginBottom: isMobile ? 32 : 64 }}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
        >
          <h2 style={{ fontSize: isMobile ? 32 : 48, fontWeight: 800, marginBottom: isMobile ? 12 : 16, color: styles.textPrimary }}>Flexible Plans for Every Business</h2>
          <p style={{ fontSize: isMobile ? 16 : 20, color: styles.textSecondary }}>Contact us for customized pricing tailored to your needs.</p>
        </motion.div>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)', 
          gap: isMobile ? 20 : 32 
        }}>
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              style={{
                background: 'rgba(10, 10, 26, 0.6)',
                backdropFilter: 'blur(16px)',
                border: plan.popular ? `2px solid ${styles.primary}` : '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: isMobile ? 16 : 24,
                padding: isMobile ? 24 : 40,
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
                  fontSize: isMobile ? 11 : 12,
                  fontWeight: 700
                }}>Most Popular</div>
              )}
              <h3 style={{ fontSize: isMobile ? 20 : 24, fontWeight: 700, marginBottom: 8, color: styles.textPrimary }}>{plan.name}</h3>
              <p style={{ fontSize: isMobile ? 13 : 14, color: styles.textSecondary, marginBottom: isMobile ? 16 : 24 }}>{plan.description}</p>
              <div style={{ marginBottom: isMobile ? 20 : 32 }}>
                <span style={{ fontSize: isMobile ? 18 : 22, fontWeight: 600, color: styles.primary }}>Contact us for pricing</span>
              </div>
              <ul style={{ listStyle: 'none', padding: 0, marginBottom: isMobile ? 20 : 32 }}>
                {plan.features.map((feature, j) => (
                  <li key={j} style={{ display: 'flex', alignItems: 'start', gap: isMobile ? 8 : 12, marginBottom: isMobile ? 8 : 12 }}>
                    <Check size={isMobile ? 16 : 20} style={{ color: styles.primary, marginTop: 2, flexShrink: 0 }} />
                    <span style={{ fontSize: isMobile ? 13 : 15, color: styles.textSecondary }}>{feature}</span>
                  </li>
                ))}
              </ul>
              <Link href="/signup" style={{ textDecoration: 'none' }}>
                <motion.div
                  style={{
                    width: '100%',
                    background: plan.popular ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : 'transparent',
                    color: plan.popular ? '#ffffff' : styles.primary,
                    padding: isMobile ? '14px 24px' : '16px 32px',
                    borderRadius: 8,
                    fontSize: isMobile ? 16 : 18,
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
                  Contact Us
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
    <div style={{ background: 'transparent', padding: isMobile ? '48px 0' : '96px 0', borderTop: '1.5px solid rgba(255, 255, 255, 0.1)' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: isMobile ? '0 16px' : '0 48px' }}>
        <motion.div
          ref={ref}
          style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.1))',
            borderRadius: isMobile ? 16 : 24,
            border: '2px solid rgba(139, 92, 246, 0.5)',
            padding: isMobile ? 32 : 64,
            textAlign: 'center',
            boxShadow: '0 20px 60px rgba(139, 92, 246, 0.2)',
          }}
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
        >
          <h2 style={{ fontSize: isMobile ? 28 : isTablet ? 36 : 48, fontWeight: 800, marginBottom: isMobile ? 12 : 16, color: styles.textPrimary }}>
            Stop Doing Repetitive Tasks Manually
          </h2>
          <p style={{ fontSize: isMobile ? 16 : 20, color: styles.textSecondary, marginBottom: isMobile ? 24 : 40, maxWidth: 700, margin: isMobile ? '0 auto 24px' : '0 auto 40px', padding: isMobile ? '0 8px' : 0 }}>
            Start automating your bookings, follow-ups, and business operations today. Free to start, no credit card required.
          </p>
          <div style={{ 
            display: 'flex', 
            flexDirection: isMobile ? 'column' : 'row',
            gap: 16, 
            alignItems: 'center', 
            justifyContent: 'center', 
            width: isMobile ? '100%' : 'auto'
          }}>
            <Link href="/signup" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: '#ffffff',
                  padding: isMobile ? '14px 24px' : '16px 32px',
                  borderRadius: 8,
                  fontSize: isMobile ? 16 : 18,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
                  width: isMobile ? '100%' : 'auto'
                }}
                whileHover={{ scale: 1.05, boxShadow: '0 6px 40px rgba(139, 92, 246, 0.6)' }}
                whileTap={{ scale: 0.95 }}
              >
                Get Started Free
                <ArrowRight size={20} />
              </motion.div>
            </Link>
            <Link href="/login" style={{ textDecoration: 'none', width: isMobile ? '100%' : 'auto' }}>
              <motion.div
                style={{
                  background: 'transparent',
                  color: styles.primary,
                  padding: isMobile ? '14px 24px' : '16px 32px',
                  borderRadius: 8,
                  fontSize: isMobile ? 16 : 18,
                  fontWeight: 600,
                  border: `2px solid ${styles.primary}`,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  width: isMobile ? '100%' : 'auto'
                }}
                whileHover={{ 
                  scale: 1.05, 
                  background: 'rgba(139, 92, 246, 0.1)',
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.3)'
                }}
                whileTap={{ scale: 0.95 }}
              >
                Sign In
              </motion.div>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function Footer() {
  const { isMobile, isTablet } = useResponsive();
  
  return (
    <div style={{ background: 'transparent', padding: isMobile ? '48px 0 32px' : '80px 0 64px', borderTop: '1px solid rgba(139, 92, 246, 0.2)' }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', padding: isMobile ? '0 16px' : '0 48px' }}>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', 
          gap: isMobile ? 32 : 64, 
          marginBottom: isMobile ? 32 : 64 
        }}>
          <div>
            <div style={{ marginBottom: 16 }}>
              <Logo />
            </div>
            <p style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, lineHeight: 1.6, margin: 0, marginBottom: isMobile ? 16 : 24 }}>
              Your AI-powered workflow automation platform. Describe what you need, we execute it automatically.
            </p>
            <div style={{ display: 'flex', gap: 12 }}>
              {['Twitter', 'LinkedIn', 'GitHub'].map((social) => (
                <motion.a
                  key={social}
                  href="#"
                  style={{
                    width: isMobile ? 32 : 36,
                    height: isMobile ? 32 : 36,
                    borderRadius: 8,
                    background: 'rgba(139, 92, 246, 0.1)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: styles.textSecondary,
                    fontSize: isMobile ? 11 : 12,
                    textDecoration: 'none',
                  }}
                  whileHover={{ 
                    background: 'rgba(139, 92, 246, 0.2)',
                    borderColor: styles.primary,
                    color: styles.primary
                  }}
                >
                  {social[0]}
                </motion.a>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 8 : 12 }}>
            <p style={{ fontSize: isMobile ? 14 : 16, color: styles.textPrimary, marginBottom: 8, fontWeight: 600 }}>Product</p>
            {[
              { name: 'Features', href: '#features' },
              { name: 'Integrations', href: '#integrations' },
              { name: 'Pricing', href: '#pricing' },
              { name: 'How It Works', href: '#how-it-works' },
            ].map((item) => (
              <motion.a
                key={item.name}
                href={item.href}
                onClick={(e) => {
                  e.preventDefault();
                  smoothScrollTo(item.href.replace('#', ''));
                }}
                style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, cursor: 'pointer', margin: 0, textDecoration: 'none' }}
                whileHover={{ color: '#8b5cf6', x: 5 }}
                transition={{ duration: 0.2 }}
              >
                {item.name}
              </motion.a>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 8 : 12 }}>
            <p style={{ fontSize: isMobile ? 14 : 16, color: styles.textPrimary, marginBottom: 8, fontWeight: 600 }}>Integrations</p>
            {['Gmail', 'Google Sheets', 'Google Calendar', 'Stripe'].map((item) => (
              <motion.p
                key={item}
                style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, cursor: 'pointer', margin: 0 }}
                whileHover={{ color: '#8b5cf6', x: 5 }}
                transition={{ duration: 0.2 }}
              >
                {item}
              </motion.p>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 8 : 12 }}>
            <p style={{ fontSize: isMobile ? 14 : 16, color: styles.textPrimary, marginBottom: 8, fontWeight: 600 }}>Legal</p>
            {['Privacy Policy', 'Terms of Service', 'Security'].map((item) => (
              <motion.p
                key={item}
                style={{ fontSize: isMobile ? 14 : 15, color: styles.textSecondary, cursor: 'pointer', margin: 0 }}
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
          flexDirection: isMobile ? 'column' : 'row',
          alignItems: isMobile ? 'flex-start' : 'center',
          justifyContent: 'space-between',
          gap: isMobile ? 12 : 0,
          paddingTop: isMobile ? 24 : 32,
          borderTop: '1.5px solid rgba(255, 255, 255, 0.1)',
        }}>
          <p style={{ fontSize: isMobile ? 12 : 14, color: styles.textMuted, margin: 0 }}>
            © 2026 Aivaro. All rights reserved.
          </p>
          <p style={{ fontSize: isMobile ? 12 : 14, color: styles.textMuted, margin: 0 }}>
            Made with 💜 for founders who hate busywork
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

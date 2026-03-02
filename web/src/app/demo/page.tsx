'use client';
import VantaBackground from '@/components/VantaBackground';
import PageTransition from '@/components/PageTransition';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowLeft, Clock } from 'lucide-react';

const styles = {
  primary: '#8b5cf6',
  textPrimary: '#e2e8f0',
  textMuted: 'rgba(226, 232, 240, 0.6)',
};

export default function DemoPage() {
  return (
    <PageTransition>
    <div style={{ 
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", 
      minHeight: '100vh',
      position: 'relative',
      overflowX: 'hidden',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <VantaBackground />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10, maxWidth: 640, width: '100%', margin: '0 auto', padding: '40px 24px', textAlign: 'center' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div style={{ marginBottom: 32 }}>
            <div style={{
              width: 64, height: 64, borderRadius: 16,
              background: 'rgba(139, 92, 246, 0.1)',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 24,
            }}>
              <Clock size={28} color={styles.primary} />
            </div>
            <h1 style={{ fontSize: 32, fontWeight: 700, color: styles.textPrimary, marginBottom: 12, lineHeight: 1.2 }}>
              New demo coming soon
            </h1>
            <p style={{ fontSize: 17, color: styles.textMuted, lineHeight: 1.6, margin: '0 0 32px' }}>
              We&apos;re recording an updated demo showcasing our latest features. Check back shortly.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{ background: styles.primary, color: '#fff', padding: '12px 24px', borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: 'pointer' }}
                whileHover={{ scale: 1.04, boxShadow: '0 0 30px rgba(139, 92, 246, 0.4)' }}
                whileTap={{ scale: 0.95 }}
              >
                Try Aivaro Free
              </motion.div>
            </Link>
            <Link href="/landing" style={{ textDecoration: 'none' }}>
              <motion.div
                style={{ display: 'flex', alignItems: 'center', gap: 6, color: styles.textMuted, padding: '12px 24px', borderRadius: 8, fontSize: 15, fontWeight: 500, border: '1px solid rgba(255,255,255,0.12)', cursor: 'pointer' }}
                whileHover={{ borderColor: 'rgba(255,255,255,0.35)', scale: 1.03 }}
                whileTap={{ scale: 0.96 }}
              >
                <ArrowLeft size={16} />
                Back to Home
              </motion.div>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
    </PageTransition>
  );
}

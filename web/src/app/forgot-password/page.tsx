'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Loader2, Mail } from 'lucide-react';

const colors = {
  primary: '#8b5cf6',
  primaryLight: '#a78bfa',
  secondary: '#6366f1',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  darkBg: '#0a0a1a',
  darkerBg: '#050510',
  inputBg: 'rgba(10, 10, 26, 0.6)',
};

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
      await fetch(`${apiBase}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      setSent(true);
    } catch {
      setSent(true); // Still show success to prevent email enumeration
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${colors.darkerBg} 0%, ${colors.darkBg} 50%, ${colors.darkerBg} 100%)`,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '24px',
      position: 'relative',
    }}>
      <Link
        href="/login"
        style={{
          position: 'absolute', top: '24px', left: '24px',
          display: 'flex', alignItems: 'center', gap: '8px',
          color: colors.textMuted, textDecoration: 'none', fontSize: '14px',
        }}
      >
        <ArrowLeft size={18} /> Back to login
      </Link>

      <div style={{
        width: '100%',
        maxWidth: '440px',
        background: 'rgba(15, 15, 35, 0.8)',
        backdropFilter: 'blur(20px)',
        borderRadius: '24px',
        border: '1px solid rgba(139, 92, 246, 0.2)',
        padding: '40px',
        textAlign: 'center',
      }}>
        <div style={{ marginBottom: '24px' }}>
          <img src="/logo.png" alt="Aivaro" style={{ height: 48, margin: '0 auto' }} />
        </div>

        {sent ? (
          <>
            <div style={{
              width: 64, height: 64, background: 'rgba(139,92,246,0.15)', borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px',
            }}>
              <Mail size={32} color="#8b5cf6" />
            </div>
            <h1 style={{ fontSize: '22px', fontWeight: 700, color: colors.textPrimary, marginBottom: '12px' }}>
              Check your email
            </h1>
            <p style={{ fontSize: '15px', color: colors.textSecondary, lineHeight: 1.6, marginBottom: '8px' }}>
              If <strong style={{ color: colors.primaryLight }}>{email}</strong> is registered, we sent a password reset link.
            </p>
            <p style={{ fontSize: '13px', color: colors.textMuted, marginBottom: '28px' }}>
              The link expires in 1 hour.
            </p>
            <Link href="/login" style={{
              display: 'inline-block', padding: '14px 32px',
              background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
              borderRadius: '12px', color: 'white', fontSize: '16px', fontWeight: 600,
              textDecoration: 'none', boxShadow: `0 4px 20px ${colors.primary}40`,
            }}>
              Back to Login
            </Link>
          </>
        ) : (
          <>
            <h1 style={{ fontSize: '22px', fontWeight: 700, color: colors.textPrimary, marginBottom: '8px' }}>
              Forgot your password?
            </h1>
            <p style={{ fontSize: '14px', color: colors.textMuted, marginBottom: '32px' }}>
              Enter your email and we&apos;ll send you a reset link.
            </p>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px', textAlign: 'left' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: colors.textSecondary, marginBottom: '8px' }}>
                  Email address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  style={{
                    width: '100%', padding: '14px 16px',
                    background: colors.inputBg, border: '1px solid rgba(139,92,246,0.2)',
                    borderRadius: '12px', color: colors.textPrimary, fontSize: '15px', outline: 'none',
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%', padding: '14px 24px',
                  background: loading ? 'rgba(139,92,246,0.5)' : `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                  border: 'none', borderRadius: '12px', color: 'white', fontSize: '16px', fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                  boxShadow: `0 4px 20px ${colors.primary}40`,
                }}
              >
                {loading && <Loader2 size={20} className="animate-spin" />}
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

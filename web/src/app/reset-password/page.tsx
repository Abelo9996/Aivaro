'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle, XCircle, Loader2, Eye, EyeOff, ArrowLeft } from 'lucide-react';

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

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'form' | 'success' | 'error'>('form');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setMessage('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
      const res = await fetch(`${apiBase}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      });
      const data = await res.json();

      if (res.ok) {
        setStatus('success');
        setMessage(data.message || 'Password reset successfully!');
      } else {
        setStatus('error');
        setMessage(typeof data.detail === 'string' ? data.detail : data.detail?.message || 'Reset failed.');
      }
    } catch {
      setStatus('error');
      setMessage('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div style={{
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${colors.darkerBg} 0%, ${colors.darkBg} 50%, ${colors.darkerBg} 100%)`,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '24px',
      }}>
        <div style={{
          background: 'rgba(15, 15, 35, 0.8)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          padding: '40px',
          maxWidth: '440px',
          width: '100%',
          textAlign: 'center',
        }}>
          <XCircle size={48} color="#ef4444" style={{ margin: '0 auto 16px' }} />
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: colors.textPrimary, marginBottom: '12px' }}>Invalid Link</h1>
          <p style={{ color: colors.textMuted, marginBottom: '24px' }}>No reset token provided.</p>
          <Link href="/login" style={{ color: colors.primaryLight, textDecoration: 'none', fontWeight: 500 }}>Back to Login</Link>
        </div>
      </div>
    );
  }

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
      overflow: 'hidden',
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
        {status === 'success' ? (
          <>
            <div style={{ width: 64, height: 64, background: 'rgba(34,197,94,0.15)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
              <CheckCircle size={32} color="#22c55e" />
            </div>
            <h1 style={{ fontSize: '22px', fontWeight: 700, color: colors.textPrimary, marginBottom: '12px' }}>Password Reset!</h1>
            <p style={{ color: colors.textSecondary, marginBottom: '28px' }}>{message}</p>
            <Link href="/login" style={{
              display: 'inline-block', padding: '14px 32px',
              background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
              borderRadius: '12px', color: 'white', fontSize: '16px', fontWeight: 600,
              textDecoration: 'none', boxShadow: `0 4px 20px ${colors.primary}40`,
            }}>
              Go to Login
            </Link>
          </>
        ) : status === 'error' ? (
          <>
            <div style={{ width: 64, height: 64, background: 'rgba(239,68,68,0.15)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
              <XCircle size={32} color="#ef4444" />
            </div>
            <h1 style={{ fontSize: '22px', fontWeight: 700, color: colors.textPrimary, marginBottom: '12px' }}>Reset Failed</h1>
            <p style={{ color: colors.textSecondary, marginBottom: '28px' }}>{message}</p>
            <Link href="/login" style={{ color: colors.primaryLight, textDecoration: 'none', fontWeight: 500 }}>Back to Login</Link>
          </>
        ) : (
          <>
            <div style={{ marginBottom: '24px' }}>
              <img src="/logo.png" alt="Aivaro" style={{ height: 48, margin: '0 auto' }} />
            </div>
            <h1 style={{ fontSize: '22px', fontWeight: 700, color: colors.textPrimary, marginBottom: '8px' }}>Set new password</h1>
            <p style={{ fontSize: '14px', color: colors.textMuted, marginBottom: '32px' }}>Enter your new password below.</p>

            {message && (
              <div style={{
                padding: '12px', borderRadius: '8px', marginBottom: '20px',
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              }}>
                <p style={{ fontSize: '14px', color: '#fca5a5', margin: 0 }}>{message}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px', textAlign: 'left' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: colors.textSecondary, marginBottom: '8px' }}>
                  New password
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    style={{
                      width: '100%', padding: '14px 48px 14px 16px',
                      background: colors.inputBg, border: '1px solid rgba(139,92,246,0.2)',
                      borderRadius: '12px', color: colors.textPrimary, fontSize: '15px', outline: 'none',
                    }}
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} style={{
                    position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer', padding: '4px',
                  }}>
                    {showPassword ? <EyeOff size={20} color={colors.textMuted} /> : <Eye size={20} color={colors.textMuted} />}
                  </button>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: colors.textSecondary, marginBottom: '8px' }}>
                  Confirm new password
                </label>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  style={{
                    width: '100%', padding: '14px 16px',
                    background: colors.inputBg, border: `1px solid ${confirmPassword && password !== confirmPassword ? 'rgba(239,68,68,0.5)' : 'rgba(139,92,246,0.2)'}`,
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
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Loader2 size={32} className="animate-spin" style={{ color: '#666' }} /></div>}>
      <ResetPasswordContent />
    </Suspense>
  );
}

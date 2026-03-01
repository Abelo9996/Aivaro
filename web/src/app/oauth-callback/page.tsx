'use client';

import { useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense } from 'react';

function OAuthCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const success = searchParams.get('success');
  const error = searchParams.get('error');

  useEffect(() => {
    const isPopup = !!window.opener;
    
    if (isPopup) {
      // Signal the parent window that OAuth is complete, then close
      try {
        window.opener.postMessage(
          { type: 'oauth_callback', success: !!success, provider: success, error },
          window.location.origin
        );
      } catch {
        // Cross-origin, parent will detect closed
      }
      setTimeout(() => window.close(), 500);
    } else {
      // Not a popup — redirect to connections page
      const params = success ? `?success=${success}` : error ? `?error=${error}` : '';
      router.replace(`/app/connections${params}`);
    }
  }, [success, error, router]);

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0a1a',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "'Inter', sans-serif",
    }}>
      <div style={{ textAlign: 'center', color: '#e2e8f0' }}>
        <p style={{ fontSize: 16, fontWeight: 500 }}>
          {success ? '✅ Connected! Redirecting...' : `❌ ${error || 'Connection failed'}`}
        </p>
      </div>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: '100vh', background: '#0a0a1a' }} />}>
      <OAuthCallbackContent />
    </Suspense>
  );
}

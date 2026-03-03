'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No verification token provided.');
      return;
    }

    const verify = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
        const res = await fetch(`${apiBase}/api/auth/verify?token=${encodeURIComponent(token)}`);
        const data = await res.json();
        
        if (res.ok) {
          setStatus('success');
          setMessage(data.message || 'Your email has been verified!');
        } else {
          setStatus('error');
          setMessage(data.detail || 'Verification failed. The link may be expired or invalid.');
        }
      } catch {
        setStatus('error');
        setMessage('Something went wrong. Please try again.');
      }
    };

    verify();
  }, [token]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
        {status === 'loading' && (
          <>
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Verifying your email...</h1>
            <p className="text-gray-500">Just a moment.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Email Verified!</h1>
            <p className="text-gray-500 mb-6">{message}</p>
            <Link
              href="/login"
              className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Go to Login
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Verification Failed</h1>
            <p className="text-gray-500 mb-6">{message}</p>
            <Link
              href="/login"
              className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Go to Login
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}

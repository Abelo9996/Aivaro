'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { WalkthroughProvider } from '@/components/walkthrough';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, checkAuth, user } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (!isLoading && isAuthenticated && user && !user.onboarding_completed) {
      router.push('/onboarding');
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const isDashboard = pathname === '/app';

  return (
    <WalkthroughProvider autoStart={isDashboard}>
      <div className="min-h-screen bg-gray-50 flex overflow-x-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col ml-64 min-w-0">
          <Header />
          {user && !user.email_verified && (
            <div className="bg-amber-50 border-b border-amber-200 px-6 py-3 flex items-center justify-between">
              <p className="text-sm text-amber-800">
                <strong>Please verify your email.</strong> Check your inbox for a verification link from Aivaro.
              </p>
              <button
                onClick={async () => {
                  try {
                    const { api } = await import('@/lib/api');
                    await api.request('/api/auth/resend-verification', { method: 'POST' });
                    alert('Verification email sent! Check your inbox.');
                  } catch {
                    alert('Failed to resend. Please try again.');
                  }
                }}
                className="text-sm font-medium text-amber-700 hover:text-amber-900 underline whitespace-nowrap ml-4"
              >
                Resend email
              </button>
            </div>
          )}
          <main className={`flex-1 ${isDashboard ? '' : 'p-6'} overflow-x-hidden`}>{children}</main>
        </div>
      </div>
    </WalkthroughProvider>
  );
}

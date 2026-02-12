'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { MessageSquare } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { WalkthroughProvider } from '@/components/walkthrough';
import GlobalAssistant from '@/components/chat/GlobalAssistant';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, checkAuth, user } = useAuthStore();
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

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

  // Only show walkthrough on dashboard page (first login experience)
  const isDashboard = pathname === '/app';

  return (
    <WalkthroughProvider autoStart={isDashboard}>
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar />
        <div className="flex-1 flex flex-col ml-64">
          <Header />
          <main className="flex-1 p-6">{children}</main>
        </div>
        
        {/* Global AI Assistant FAB */}
        <button
          onClick={() => setIsAssistantOpen(true)}
          className="fixed bottom-6 right-6 w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105 flex items-center justify-center z-40 group"
          title="AI Assistant"
        >
          <MessageSquare className="w-5 h-5 group-hover:scale-110 transition-transform" />
        </button>
        
        {/* Global Assistant Panel */}
        <GlobalAssistant 
          isOpen={isAssistantOpen} 
          onClose={() => setIsAssistantOpen(false)} 
        />
      </div>
    </WalkthroughProvider>
  );
}

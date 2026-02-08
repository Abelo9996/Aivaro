'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Workflow, Loader2 } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/app');
    } else {
      router.push('/landing');
    }
  }, [router]);

  // Show loading state while determining where to redirect
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-4 rounded-xl inline-block mb-4">
          <Workflow className="w-8 h-8 text-white" />
        </div>
        <div className="flex items-center justify-center space-x-2 text-gray-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading Aivaro...</span>
        </div>
      </div>
    </div>
  );
}


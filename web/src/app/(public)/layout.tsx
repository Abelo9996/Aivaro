'use client';

import PageTransition from '@/components/PageTransition';

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <PageTransition>
      {children}
    </PageTransition>
  );
}

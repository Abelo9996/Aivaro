'use client';

import VantaBackground from '@/components/VantaBackground';
import PageTransition from '@/components/PageTransition';

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <VantaBackground />
      <PageTransition>
        {children}
      </PageTransition>
    </>
  );
}

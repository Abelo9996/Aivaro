'use client';

import { AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import PageTransition from '@/components/PageTransition';

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div style={{ overflow: 'hidden', position: 'relative', minHeight: '100vh' }}>
      <AnimatePresence mode="wait">
        <PageTransition key={pathname}>
          {children}
        </PageTransition>
      </AnimatePresence>
    </div>
  );
}

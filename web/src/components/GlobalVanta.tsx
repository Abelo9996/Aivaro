'use client';

import { usePathname } from 'next/navigation';
import { useEffect, useRef } from 'react';

const VANTA_ROUTES = ['/login', '/signup', '/forgot-password', '/reset-password', '/demo', '/terms', '/privacy', '/verify', '/landing'];

export default function GlobalVanta() {
  const pathname = usePathname();
  const vantaRef = useRef<HTMLDivElement>(null);
  const vantaEffect = useRef<any>(null);
  const initialized = useRef(false);

  const show = VANTA_ROUTES.some(r => pathname === r || pathname.startsWith(r + '/'));

  useEffect(() => {
    if (typeof window === 'undefined' || initialized.current) return;
    initialized.current = true;

    const loadScript = (src: string): Promise<void> =>
      new Promise((resolve, reject) => {
        if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
        const s = document.createElement('script');
        s.src = src;
        s.onload = () => resolve();
        s.onerror = reject;
        document.head.appendChild(s);
      });

    const init = async () => {
      await loadScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js');
      await loadScript('https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.topology.min.js');
      let attempts = 0;
      while (!(window as any).VANTA && attempts < 50) {
        await new Promise(r => setTimeout(r, 100));
        attempts++;
      }
      if (!vantaRef.current || vantaEffect.current || !(window as any).VANTA) return;
      vantaEffect.current = (window as any).VANTA.TOPOLOGY({
        el: vantaRef.current,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.0,
        minWidth: 200.0,
        scale: 1.0,
        scaleMobile: 1.0,
        color: 0x8b5cf6,
        backgroundColor: 0x0a0a1a,
      });
    };
    init();
  }, []);

  return (
    <div
      ref={vantaRef}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 0,
        visibility: show ? 'visible' : 'hidden',
        pointerEvents: 'none',
      }}
    />
  );
}

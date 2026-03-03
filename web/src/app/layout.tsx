import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import GlobalVanta from '@/components/GlobalVanta';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'Aivaro',
    template: '%s | Aivaro',
  },
  description: 'Tell us what you need in plain English. We build and run your business workflows automatically. Not suggestions. Not drafts. Execution.',
  icons: {
    icon: '/favicon.png',
    shortcut: '/favicon.png',
    apple: '/favicon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.png" type="image/png" />
      </head>
      <body className={inter.className}>
        <GlobalVanta />
        {children}
      </body>
    </html>
  );
}

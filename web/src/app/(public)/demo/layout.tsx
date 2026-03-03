import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Aivaro Demo - See AI Workflow Automation in Action',
  description: 'Watch how Aivaro transforms plain English into powerful automated workflows. AI-powered automation for Gmail, Google Sheets, Calendar, and Stripe integrations.',
  openGraph: {
    title: 'Aivaro Demo - See AI Workflow Automation in Action',
    description: 'Watch how Aivaro transforms plain English into powerful automated workflows. No coding required — just describe what you need.',
    type: 'video.other',
    url: 'https://aivaro.io/demo',
    videos: [
      {
        url: 'https://aivaro.io/Aivaro.mp4',
        width: 1920,
        height: 1080,
        type: 'video/mp4',
      },
    ],
    images: [
      {
        url: 'https://aivaro.io/og-demo.png',
        width: 1200,
        height: 630,
        alt: 'Aivaro - AI Workflow Automation Demo',
      },
    ],
  },
  twitter: {
    card: 'player',
    title: 'Aivaro Demo - See AI Workflow Automation in Action',
    description: 'Watch how Aivaro transforms plain English into powerful automated workflows.',
    players: [
      {
        playerUrl: 'https://aivaro.io/demo',
        streamUrl: 'https://aivaro.io/Aivaro.mp4',
        width: 1920,
        height: 1080,
      },
    ],
  },
};

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

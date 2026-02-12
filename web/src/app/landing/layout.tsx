import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Your AI Co-Founder',
};

export default function LandingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

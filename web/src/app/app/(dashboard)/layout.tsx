import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboard',
};

export default function AppMainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

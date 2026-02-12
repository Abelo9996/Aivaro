import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Executions',
};

export default function ExecutionsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

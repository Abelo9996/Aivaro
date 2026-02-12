import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Workflows',
};

export default function WorkflowsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

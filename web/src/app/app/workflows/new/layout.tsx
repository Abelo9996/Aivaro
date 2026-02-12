import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'New Workflow',
};

export default function NewWorkflowLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

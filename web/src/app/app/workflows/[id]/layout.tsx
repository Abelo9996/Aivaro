import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Workflow Editor',
};

export default function WorkflowEditorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

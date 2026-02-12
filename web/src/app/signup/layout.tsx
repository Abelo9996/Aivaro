import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign Up',
};

export default function SignupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

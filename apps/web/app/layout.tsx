import type { Metadata } from 'next';
import type { ReactNode } from 'react';

export const metadata: Metadata = {
  title: 'Primordia',
  description: 'A desktop evolution laboratory — challenges and leaderboards.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'system-ui', margin: 0, background: '#0b1020', color: '#e6edf3' }}>
        {children}
      </body>
    </html>
  );
}

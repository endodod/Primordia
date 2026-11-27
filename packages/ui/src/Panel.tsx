import type { ReactNode } from 'react';

export interface PanelProps {
  title: string;
  children: ReactNode;
}

/** Simple titled container. Placeholder until the real design system lands. */
export function Panel({ title, children }: PanelProps) {
  return (
    <section style={{ border: '1px solid #30363d', borderRadius: 8, padding: 16, minWidth: 240 }}>
      <h2 style={{ marginTop: 0, fontSize: 18 }}>{title}</h2>
      {children}
    </section>
  );
}

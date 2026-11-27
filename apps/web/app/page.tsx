import { Panel } from '@primordia/ui';

export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: '0 auto', padding: 32 }}>
      <h1>🧬 Primordia</h1>
      <p>A desktop evolution laboratory. Design creatures, build worlds, watch them evolve.</p>
      <Panel title="Leaderboard">
        <p>Challenges and verified leaderboards arrive in Phase 4.</p>
      </Panel>
    </main>
  );
}

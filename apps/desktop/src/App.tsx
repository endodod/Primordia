import { useEffect, useRef, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Panel } from '@primordia/ui';

interface Snapshot {
  tick: number;
  hash: string;
  dots: [number, number][];
}

const WORLD_SIZE = 1000;

/** Phase 0 shell: renders the engine's dots and advances the simulation every frame. */
export function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [running, setRunning] = useState(true);

  useEffect(() => {
    if (!running) return;
    let frame = 0;
    const loop = async () => {
      const next = await invoke<Snapshot>('step', { ticks: 1 });
      setSnapshot(next);
      frame = requestAnimationFrame(loop);
    };
    frame = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frame);
  }, [running]);

  useEffect(() => {
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx || !snapshot) return;
    const { width, height } = ctx.canvas;
    ctx.fillStyle = '#0b1020';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#7ee787';
    for (const [x, y] of snapshot.dots) {
      ctx.beginPath();
      ctx.arc((x / WORLD_SIZE) * width, (y / WORLD_SIZE) * height, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [snapshot]);

  return (
    <main style={{ display: 'flex', gap: 16, padding: 16, fontFamily: 'system-ui' }}>
      <canvas ref={canvasRef} width={600} height={600} style={{ borderRadius: 8 }} />
      <Panel title="Primordia Lab">
        <p>Tick: {snapshot?.tick ?? 0}</p>
        <p>
          State hash: <code>{snapshot?.hash ?? '—'}</code>
        </p>
        <button onClick={() => setRunning((r) => !r)}>{running ? 'Pause' : 'Play'}</button>
      </Panel>
    </main>
  );
}

# 🧬 Primordia

A science-first, local-first **evolution laboratory**. Design creatures, release them into worlds
you build, set the laws of nature, and observe what evolution does with them.

- **Desktop app** (Tauri v2 + React) — the lab, works fully offline
- **Engine** (Rust) — deterministic simulation core, native + WASM
- **Website** (Next.js) — landing page and, from Phase 4, a verified challenge leaderboard
- **Docs** (Docusaurus) — user guide, ADRs, devlog

> Status: Phase 0 — Foundation. See the [roadmap](docs/roadmap.md).

## Repo layout

```
engine/          Rust simulation core (pure, deterministic)
apps/desktop/    Tauri desktop lab
apps/web/        Website + leaderboard
apps/docs/       Docs site + devlog
packages/ui/     Shared React components
packages/types/  TS types shared with Rust (generated from Phase 1)
docs/            Roadmap and design docs
scripts/         One-off maintenance scripts (GitHub setup)
```

## Getting started

```bash
pnpm install
cargo test -p primordia-engine
cargo tauri dev                        # desktop app (needs Tauri prerequisites)
pnpm dev --filter @primordia/web       # website
pnpm dev --filter @primordia/docs      # docs site
```

## Contributing

Read [`HOW-WE-WORK.md`](HOW-WE-WORK.md) first, then [`DEV.md`](DEV.md).
Working with Claude Code? It follows [`CLAUDE.md`](CLAUDE.md).

Team notes, meeting notes, research and playtest logs live in the team's Notion workspace
(Primordia hub).

## License

To be decided (MIT or Apache-2.0) — see roadmap §12.

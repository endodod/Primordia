# apps/web/CLAUDE.md

Rules for the website / leaderboard. These add to the root `CLAUDE.md` §9.

- Until Phase 4 this is only a landing page. Do not add accounts, social features or a database
  before the Phase 4 ADR.
- Server components by default; client components only when needed.
- The verification API (Phase 4) re-simulates submitted run files with `engine.wasm`. Never
  accept a client-computed score.
- Validate all API input at the boundary. No secrets in client code.

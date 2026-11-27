# engine/CLAUDE.md

Rules for working in the engine crate. These add to the root `CLAUDE.md` §7.

- This crate must stay pure: no `std::fs`, `std::net`, `std::time`, threads, logging side
  effects, Tauri or rendering code. It compiles to `wasm32-unknown-unknown`.
- All randomness through the world's `ChaCha8Rng`. Never `thread_rng` or OS entropy.
- Integer math only until ADR-0002 decides the numeric strategy.
- Any change that alters outcomes for the same inputs: bump `ENGINE_VERSION`, regenerate the
  golden hashes (`UPDATE_GOLDEN=1 cargo test -p primordia-engine --test determinism`), and
  explain the change in the PR. Never regenerate golden hashes to "fix" a failing test without
  understanding why it failed.
- Run before committing: `cargo fmt --all`, `cargo clippy -p primordia-engine -- -D warnings`,
  `cargo test -p primordia-engine`.

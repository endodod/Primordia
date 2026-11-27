---
title: 'ADR-0001: Local-first app with verified leaderboard'
---

# ADR-0001: Local-first desktop app with a verified online leaderboard

- **Status:** Accepted
- **Date:** 2026-11-27
- **Deciders:** team (feedback round 1)

## Context
We want a big, presentable project that is free to host and maintain. The first draft had a
community web platform with Kafka, accounts and social features, which needed always-on
infrastructure and moderation.

## Decision
- The **desktop app (Tauri v2)** is the whole product and works offline.
- A shared, pure **Rust engine crate** is deterministic: same run file ⇒ identical result on all
  platforms.
- The only online part is a **challenge leaderboard** (Next.js on Vercel + one free database).
  Clients submit run files, never scores; the server re-simulates them with the engine compiled
  to WASM.
- Removed: Kafka, Docker, accounts, publishing, comments, follows, live spectating.

## Consequences
- Hosting is effectively free; nothing to babysit.
- Determinism becomes the most important technical property — enforced by cross-platform CI.
- Run files need a versioned format from day one.
- Social features can be revisited after v1.0 if there is demand.

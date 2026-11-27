# Primordia — Roadmap

*Version 1.0 of this roadmap · incorporates team feedback round 1*

This is the plan from empty repo to v1.0 and beyond. It is a living document: we re-plan at the
start of every phase, and changes go through a PR like everything else.

---

## Contents

1. [Vision](#1-vision)
2. [Principles](#2-principles)
3. [What changed since the first draft](#3-what-changed-since-the-first-draft)
4. [Architecture at a glance](#4-architecture-at-a-glance)
5. [Cross-cutting requirements](#5-cross-cutting-requirements)
6. [Scope & the v1.0 cut line](#6-scope--the-v10-cut-line)
7. [Phases](#7-phases)
   - [Phase 0 — Foundation](#phase-0--foundation)
   - [Phase 1 — First Life (v0.1)](#phase-1--first-life-v01)
   - [Phase 2 — The Lab (v0.2)](#phase-2--the-lab-v02)
   - [Phase 3 — Local Gallery (v0.3)](#phase-3--local-gallery-v03)
   - [Phase 4 — Challenges & Leaderboard (v0.4)](#phase-4--challenges--leaderboard-v04)
   - [Phase 5 — Launch (v1.0)](#phase-5--launch-v10)
   - [Phase 6 — Brains (v2.0)](#phase-6--brains-v20)
8. [Post-v1.0 backlog](#8-post-v10-backlog)
9. [Timeline](#9-timeline)
10. [Roles](#10-roles)
11. [Risks](#11-risks)
12. [Open questions](#12-open-questions)

---

## 1. Vision

**A desktop evolution laboratory.** You design creatures in the lab, release them into a world
you built, set the laws of nature, and observe what evolution does with them — with the tools of
a scientist: controlled experiments, reproducible runs, batch statistics and data export.

The only online part is a **challenge leaderboard**: anyone can submit a run, and the server
verifies it by re-running it with the exact same engine. No trust required.

**Feel:** closer to a research instrument than a game. Fun comes from discovery, not from
points — though challenges give it a competitive edge.

---

## 2. Principles

1. **Science first.** Every feature should help you *design, run, observe or analyze* an
   experiment. Visuals serve understanding.
2. **Local first.** The desktop app is the whole product. It works offline, forever, with no account.
3. **Deterministic.** Seed + config + inputs + engine version ⇒ bit-identical result on every
   platform. This is what makes replays, remixes, comparisons and the leaderboard possible.
4. **Reproducible by default.** Every run is a small file anyone can re-run.
5. **Free to run.** No infrastructure we have to pay for or babysit.
6. **Clean and presentable.** We work like a real team: issues, PRs, reviews, CI, docs, devlog
   (see `DEV.md`).

---

## 3. What changed since the first draft

| Area | First draft | Now | Why |
|---|---|---|---|
| Product shape | Desktop lab + community web platform | **Self-contained desktop app + online leaderboard only** | Smaller scope, robust, no moderation-heavy social layer |
| Tone | Game-like | **Science-like** | Team feedback |
| Creature creation | Start species set in world config | **Creature Designer in the lab → release into your world** | Team feedback |
| Kafka | Event backbone | ❌ Removed | No backend that needs it |
| Docker, Neon, Aiven, Oracle | Hosting stack | ❌ Removed | Nothing to host except the leaderboard |
| Accounts, publishing, profiles, comments, follows, likes, notifications | Phase 3 | ❌ Removed | Out of scope for v1.0 |
| Live spectating | Phase 4 | ❌ Removed | Requires servers |
| Events & conditions | Phase 4 | **Phase 2** | Core to experiments |
| Batch runs | Phase 2 | Phase 2, **multi-threaded in-app** | Science use case |
| Run file format | Not specified | **Versioned format from Phase 1** | Old runs must keep opening |
| Performance | Not specified | **Explicit targets, benchmarked in CI** | Engine needs a design goal |
| Leaderboard trust | Server re-runs | **Server re-runs in WASM with fixed tick limits** | Fits a Vercel function |
| New features | — | Biomes, barriers, day/night, seasons, speciation, gene heatmap, disease, plant evolution, group behavior | Team wishlist |

---

## 4. Architecture at a glance

```
┌──────────────────────────── Desktop app (Tauri v2) ────────────────────────────┐
│                                                                                 │
│  React + TS UI                         Rust side                                │
│  ├─ Creature Designer                  ├─ engine crate (native, multi-threaded  │
│  ├─ World & Rules Editor               │   batch runs)                          │
│  ├─ Run view (PixiJS)        ◄──IPC──► ├─ run files (versioned)                 │
│  ├─ Analysis (charts, heatmaps)        ├─ SQLite (gallery index, results)       │
│  ├─ Gallery / Replays                  └─ export (CSV / Parquet)                │
│  └─ Challenges                                                                  │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ submit run file (seed, config, inputs)
                                       ▼
┌──────────────────────── Leaderboard (Vercel, Next.js) ─────────────────────────┐
│  API route: verify signature → re-run in engine.wasm → compute score → store    │
│  Pages: challenges, leaderboards, (optional) top-run replays in WASM            │
│  Free database: scores, challenges, display names + public keys                 │
└─────────────────────────────────────────────────────────────────────────────────┘

Docs + devlog: Docusaurus on GitHub Pages · Installers: GitHub Releases
```

### Repo layout
```
engine/          Rust crate — pure, deterministic, no Tauri/IO/rendering
apps/desktop/    Tauri v2 + React + TS
apps/web/        Next.js — leaderboard, challenge pages, landing page
apps/docs/       Docusaurus — docs, ADRs, devlog
packages/ui/     Shared React components (charts, renderer) used by desktop + web
.github/         CI, templates, CODEOWNERS
```

---

## 5. Cross-cutting requirements

These apply to every phase and are part of every phase's definition of done.

### 5.1 Determinism
- All randomness from a seeded RNG owned by the world.
- Time = ticks. Fixed timestep. No wall-clock time in simulation logic.
- No order-dependent iteration over hash maps/sets.
- **Numeric strategy decided in week 1 of Phase 1** (fixed-point vs. strict floats — see §12).
- **Cross-platform CI:** same seed on Windows, macOS, Linux and WASM ⇒ identical state hash.
- Outcome-changing changes bump `ENGINE_VERSION`.

### 5.2 Run file format
- Contains: format version, engine version, seed, world config, rules, creature designs,
  timestamped interventions (tick-indexed), metadata (name, notes, created at).
- **Versioned from day one** (`format_version`). Every new version ships with a migration from
  the previous one. Old files must always open.
- Replays are re-simulation, so files stay tiny (KBs, not MBs). Optional cached snapshots for
  fast seeking.
- Engine version pinning: if a run was made with an older engine, the app says so and either
  replays with a compatible engine or clearly marks results as "re-simulated with vX".
- Format documented in `docs/run-format.md`, with an example file.

### 5.3 Performance targets
Baseline machine: a mid-range laptop from the last ~4 years (to be defined concretely in Phase 1).

| Scenario | Target |
|---|---|
| Rendered run | 2,000 creatures at 60 fps, 1× – 10× speed |
| Headless run | 10,000 creatures at ≥ 200 ticks/s |
| Batch runs | Scale near-linearly with CPU cores |
| Leaderboard verification (WASM) | Challenge run completes well within the Vercel function time limit on the free plan (target < 10 s) |

- **Status: agreed as provisional targets.** Confirmed or adjusted at the end of Phase 1 based
  on real measurements.
- Benchmarks in CI (engine crate) with regression alerts.

### 5.4 Science features
- Every run records full statistics; everything visible in a chart is exportable (CSV, optionally Parquet).
- Batch runs report aggregate statistics (mean, spread, confidence intervals) across seeds.
- An experiment notes field: hypothesis, setup, observations — saved in the run file.

### 5.5 Privacy & moderation (leaderboard only)
- Identity = display name + public key generated by the app. No email, no password.
  Optional "sign in with GitHub" later.
- We store only: display name, public key, submitted runs, scores, timestamps.
- Short privacy note on the website and in the app before first submission.
- Display names and run titles pass an offensive-word filter; admin can hide entries.
- Rate limiting per key and per IP.

### 5.6 Licensing & contributions
- Code license decided in Phase 0 (**MIT or Apache-2.0** — see §12).
- `CONTRIBUTING.md` (derived from `DEV.md`), `CODE_OF_CONDUCT.md`, issue/PR templates.
- Third-party assets (if any) must be CC0 or compatible; tracked in `CREDITS.md`.

### 5.7 Quality bar (from `DEV.md`)
Branch protection, CI green, reviews, tests, docs updated, devlog post per sprint.

---

## 6. Scope & the v1.0 cut line

### Must (v1.0 ships with these, even if everything else slips)
- Deterministic engine, cross-platform verified, versioned run files
- Creature Designer → release into world
- Biomes with barriers (rivers, mountains)
- Seasons and day/night cycle
- Speciation with automatic species detection
- Rules editor, world editor, events & conditions, recorded interventions
- Analysis: population charts, gene distributions, **gene heatmap over time**, species tree
- Batch runs with aggregate statistics, data export
- Local gallery, replays, remixing own runs
- Installers for Windows, macOS, Linux; docs site; license

### Should (v1.0 if time allows — otherwise v1.1)
- Challenges & online leaderboard (Phase 4)
- Disease / parasites
- Creature inspector with full ancestry
- Snapshot seeking / rewind

### Could (nice to have)
- Achievements / experiment milestones ("first predator," "10,000 generations")
- Watching top leaderboard runs as replays on the web
- Sign in with GitHub

### Later (post-v1.0)
- Plant evolution (defenses, arms race)
- Group behavior (herding, pack hunting, kin help)
- Neural-network brains (Phase 6)

**Cut line:** if we're behind at the end of Phase 3, Phase 4 becomes v1.1 and we go straight to
Phase 5 with the Must list.

---

## 7. Phases

Each phase lists: goal · deliverables · definition of done · dependencies · risks · estimate.
Estimates are in weeks at a hobby pace and **exclude** the buffer (see §9).

---

### Phase 0 — Foundation
**Goal:** everyone can clone, build and contribute; a dot moves on screen.

**Deliverables**
- Repo with monorepo structure (Cargo workspace + pnpm/Turborepo)
- `CLAUDE.md`, `DEV.md`, `CONTRIBUTING.md`, license, code of conduct
- Branch protection, CODEOWNERS, issue + PR templates
- CI: fmt, lint, typecheck, tests, Tauri build (Linux on PRs)
- Empty `engine` crate — no Tauri code — consumed by `apps/desktop`
- Tauri app shell that renders **one moving dot** driven by the engine tick loop
- Docusaurus site on GitHub Pages with devlog post #0
- GitHub Project board, milestones v0.1–v1.0, first issues for Phase 1
- ADR-0001: architecture (local-first + verified leaderboard)

**Setup for a new member:** clone → `pnpm install` → `cargo tauri dev`. That's it.

**Definition of done**
- [ ] Fresh clone builds and runs on Windows, macOS and Linux
- [ ] CI green on `dev`, branch protection active
- [ ] Dot moves on screen, position comes from the engine
- [ ] Docs site live, devlog #0 published

**Depends on:** team formed, roles assigned · **Risks:** Tauri setup differences per OS
**Estimate:** 1 week

---

### Phase 1 — First Life (v0.1)
**Goal:** creatures exist, eat, reproduce and evolve — deterministically, everywhere.

**Deliverables**
- **Numeric strategy decided** (fixed-point vs strict floats) — ADR-0002, week 1
- Engine core: world grid, food, creatures, energy, movement, eating, reproduction, death
- Seeded RNG, fixed timestep, `ENGINE_VERSION`
- Simple genome: size, speed, diet, vision, aggression, mutation
- Rule-based `Brain` trait implementation (separate from genome — ready for Phase 6)
- Procedural rendering: creatures drawn from genes (PixiJS)
- **Basic Creature Designer:** set genes for a starting creature, release it into the world
- Run controls: play, pause, speed (1×, 10×, headless max)
- Charts: population over time, gene distributions; **first version of the gene heatmap**
- **Run file format v1** + save / load, documented
- **Cross-platform determinism CI** (Win/macOS/Linux/WASM hash comparison)
- **Performance benchmarks in CI** + measured baseline vs. targets

**Definition of done**
- [ ] A designed creature released into a world evolves visibly over generations
- [ ] Same run file ⇒ identical hash on all four platforms in CI
- [ ] Save → close → load → replay produces the identical run
- [ ] Benchmarks run in CI; baseline documented; targets confirmed or adjusted
- [ ] Run format documented with example
- [ ] Devlog posts for each sprint

**Depends on:** Phase 0 · **Risks:** float determinism across platforms (biggest technical risk
of the project — tackle first), rendering performance
**Estimate:** 4 weeks

---

### Phase 2 — The Lab (v0.2)
**Goal:** the desktop app becomes a real scientific instrument.

**Deliverables**

*Creature Designer (full)*
- Design multiple species, save them as templates, release them at chosen locations/times
- Preview: how the design will look and its baseline stats

*World & environment*
- World editor: paint terrain, place food sources, set world size
- **Biomes:** forest, desert, water, tundra — each with food yield, temperature, movement cost
- **Barriers:** rivers, mountains — split populations (enables allopatric speciation)
- **Day/night cycle:** affects vision and activity
- **Seasons:** food growth varies over the year

*Rules*
- Rules editor: mutation rate/strength, reproduction cost, carrying capacity, predation, aging
- Presets ("Earth-like," "Harsh," "Abundant")

*Evolution*
- **Speciation:** genetic distance metric; breeding blocked beyond a threshold; new species
  detected and auto-named
- Species tree (phylogeny) view

*Events & conditions* (moved from Phase 4)
- Scheduled events: ice age, drought, meteor, invasive species
- Triggered rules ("if population > N, start drought")
- **Live interventions recorded as tick-indexed inputs** in the run file

*Experiments*
- **Batch runs:** same setup across N seeds, multi-threaded, with aggregate statistics
- Side-by-side comparison of runs
- Experiment notes (hypothesis / observations) saved with the run
- **Data export** (CSV) for all charts and raw stats
- Gene heatmap polished: per gene, per species, over generations

**Definition of done**
- [ ] A user can: design species → build a biome world with barriers → set rules → schedule an
      ice age → run → intervene → analyze → export data
- [ ] Interventions replay identically
- [ ] A river barrier can produce two distinct species from one ancestor (demonstrated in a devlog)
- [ ] Batch of 20 seeds runs in parallel and reports aggregate stats
- [ ] Run file format v2 with migration from v1
- [ ] Determinism + performance CI still green

**Depends on:** Phase 1 · **Risks:** scope (largest phase — split into 2 sprints with a review
in between), speciation tuning, performance with biomes
**Estimate:** 5 weeks

---

### Phase 3 — Local Gallery (v0.3)
**Goal:** your runs become a browsable, re-playable library.

**Deliverables**
- Gallery of all local runs (SQLite index): thumbnail, summary, tags, notes, search/filter
- Replay viewer with timeline and seeking (cached snapshots)
- **Remix:** duplicate any run, change variables, run again — linked as "derived from"
- Auto-generated run summary ("3 species, 1 extinction, predators at gen 340")
- Creature inspector: genes, ancestry, cause of death
- Import/export run files (share a file with a friend manually)

**Definition of done**
- [ ] 100+ runs browse smoothly
- [ ] Any run replays identically and can be remixed
- [ ] Shared run file opens on another machine with identical results
- [ ] **Cut-line check:** decide whether Phase 4 goes into v1.0 or v1.1

**Depends on:** Phase 2 (run format v2) · **Risks:** snapshot storage size
**Estimate:** 2 weeks

---

### Phase 4 — Challenges & Leaderboard (v0.4)
**Goal:** a small, honest online competition. The only online part of the project.

**Deliverables**
- Set up Vercel project + free database (choice in ADR at phase start)
- Challenge format: fixed world/rules + goal + **fixed tick limit** + scoring function
- Challenges shipped in the app and listed on the website
- App identity: display name + generated key pair; submissions signed
- **Submit a run:** app sends the run file (seed, config, inputs) — never the score
- **Server verification:** API route loads `engine.wasm`, re-runs the submission, computes the
  score, stores it
- Leaderboard pages on the website (Next.js)
- Rate limiting, offensive-name filter, admin hide
- Privacy note in app and on website
- *(Could)* replay top runs on the website via WASM
- *(Could)* achievements / experiment milestones, verified the same way

**Definition of done**
- [ ] A submitted run is re-simulated server-side and its score matches the local score
- [ ] A tampered run file is rejected or scored correctly (never trusted)
- [ ] Verification fits within the free plan's function limits with margin
- [ ] Leaderboard live; privacy note published
- [ ] At least 3 challenges

**Depends on:** Phase 3, WASM build from Phase 1 · **Risks:** WASM performance in serverless,
engine version mismatch between app and server (server must keep old engine versions or pin
challenges to an engine version)
**Estimate:** 3 weeks

---

### Phase 5 — Launch (v1.0)
**Goal:** polished, installable, documented, tested by outsiders.

**Deliverables**
- Bug fixing, performance pass, UI polish, onboarding (first-run tutorial experiment)
- Installers for Windows, macOS, Linux on **GitHub Releases**, Tauri auto-updater
- **Code-signing decision** (ADR): pay (Apple Developer account for notarization, Windows
  certificate) or accept warnings and document how to install
- **Closed beta** with 5–10 outside testers; feedback round; fixes
- Complete docs: user guide, science background (how evolution is modeled), run format,
  challenge rules, developer docs
- Landing page (on the web app) with screenshots/GIFs and download links
- License finalized, `CREDITS.md`, privacy note
- Launch devlog post 🎉

**Definition of done**
- [ ] Beta feedback addressed (P0/P1 issues closed)
- [ ] Installers work on clean machines for all three OSes
- [ ] All Must items from §6 shipped
- [ ] Docs complete; landing page live
- [ ] v1.0.0 tagged and released

**Depends on:** Phase 3 (Phase 4 optional per cut line) · **Risks:** installer/signing issues,
beta finding big problems late
**Estimate:** 3 weeks

---

### Phase 6 — Brains (v2.0)
**Goal:** creatures that learn.

- Neural-network brains implementing the existing `Brain` trait
- Network weights as part of the genome, evolved through mutation (neuroevolution)
- Brain inspector / visualization
- New engine version; old runs keep replaying with rule-based brains
- Enables group behavior (herding, pack hunting) emerging naturally

**Estimate:** open-ended — planned after v1.0

---

## 8. Post-v1.0 backlog

| Feature | Notes |
|---|---|
| Plant evolution | Toxins, spikes, growth strategies — arms race with grazers |
| Group behavior | Herding, pack hunting, kin help — easier with brains |
| Disease / parasites | If not in v1.0: contact spread, co-evolution, population crashes |
| Sign in with GitHub | Optional identity upgrade for the leaderboard |
| Top-run replays on web | If not in Phase 4 |
| Achievements | If not in Phase 4 |
| Sharing runs online | Would revisit the community idea — only if there's demand |

---

## 9. Timeline

| Phase | Estimate | With 30% buffer | Cumulative (buffered) |
|---|---|---|---|
| 0 — Foundation | 1 wk | 1.5 wk | 1.5 wk |
| 1 — First Life | 4 wk | 5 wk | 6.5 wk |
| 2 — The Lab | 5 wk | 6.5 wk | 13 wk |
| 3 — Local Gallery | 2 wk | 2.5 wk | 15.5 wk |
| 4 — Challenges & Leaderboard | 3 wk | 4 wk | 19.5 wk |
| 5 — Launch | 3 wk | 4 wk | **23.5 wk** |

- **≈ 4.5 – 5.5 months to v1.0** at a hobby pace, including buffer.
- **Without Phase 4** (cut line): ≈ 4.5 months.
- Phases 1–2 are the riskiest; if they overrun by more than the buffer, re-plan instead of crunching.
- Estimates get refined at each phase kickoff once we know the team's real velocity.

---

## 10. Roles

With the backend gone, there are three main areas. Final assignment once the team is settled.

| Area | Responsibilities | Owner | Backup |
|---|---|---|---|
| **Engine** | Simulation, genetics, speciation, determinism, performance, WASM build | | |
| **Desktop app** | Designer, editors, run view, analysis/charts, gallery, batch UI | | |
| **Leaderboard + docs** | Next.js site, verification API, database, docs site, release pipeline | | |

If there are more than three people, split **Desktop** into *Lab UI* (designer, editors, gallery)
and *Visualization & analysis* (renderer, charts, heatmaps, export). Everyone writes devlog posts
on rotation.

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Cross-platform float non-determinism | High | Critical | Decide numeric strategy week 1; cross-platform hash CI from Phase 1 |
| Phase 2 scope explosion | High | High | Split into two sprints; Must/Should per feature; cut line |
| Engine performance below targets | Medium | High | Benchmarks in CI from Phase 1; spatial partitioning; profile early |
| Simulation is boring / collapses | Medium | High | Regular playtesting; presets; tuning sprints |
| WASM verification too slow for serverless | Medium | Medium | Fixed tick limits; benchmark in Phase 1; challenge sizes capped |
| Engine version drift (app vs server) | Medium | Medium | Challenges pinned to engine version; server keeps old versions |
| Unsigned installers scare users | High | Low–Medium | Decide in Phase 5; document install steps |
| Team availability drops | Medium | High | Backups per area; small PRs; good docs |
| Over-reliance on Claude for the engine | Medium | Medium | Engine owner understands it deeply; pair reviews |

---

## 12. Open questions

To decide before or during the named phase:

| Question | Options | Decide by | Who |
|---|---|---|---|
| Numeric strategy | Fixed-point vs. strict floats | Phase 1, week 1 | Engine owner (ADR) |
| Leaderboard: scores only, or also replay top runs on the web? | Scores only / + replays | Phase 4 kickoff | Team |
| Database for scores | e.g. Neon, Turso, Supabase (free tiers) | Phase 4 kickoff | Leaderboard owner (ADR) |
| License | MIT / Apache-2.0 / dual | Phase 0 | Team |
| Code signing | Pay / accept warnings | Phase 5 | Team |
| Is disease/parasites in v1.0? | v1.0 / later | Phase 2 review | Team |
| Achievements: in or out? Fits "science-like"? | Phase 4 Could / post-v1.0 | Phase 4 kickoff | Team |
| Project name | ✅ Primordia | Phase 0 | Team |
| Who owns which area? | see §10 | Phase 0 | Team |

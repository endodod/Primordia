# CLAUDE.md

Instructions for Claude Code in this repository. Read this fully before starting any task.
Human-facing process docs live in `DEV.md`, `HOW-WE-WORK.md` and `docs/` (start with
`docs/roadmap.md`). If anything here conflicts with a direct instruction from the developer you
are working with, ask before acting.

---

## 1. Project overview

**Primordia** is a **science-first, local-first evolution simulation**.

- **Desktop app (the whole product):** users design creatures in the Creature Designer, release
  them into worlds they build (biomes, barriers, seasons, day/night), set the rules of evolution,
  schedule events, run experiments (incl. multi-threaded batch runs), analyze and export data,
  and browse a local gallery of runs. Works fully offline, no account.
- **Leaderboard (the only online part):** a small Next.js app on Vercel. Users submit a **run
  file** (never a score) for a challenge; the server re-runs it with the same engine compiled to
  WASM and computes the score itself.
- **Determinism is the foundation:** seed + config + creature designs + tick-indexed
  interventions + engine version ⇒ bit-identical result on Windows, macOS, Linux and WASM.
  Replays, remixes, comparisons and leaderboard verification all depend on it.
- **Tone:** a research instrument, not a game. Features should help users design, run, observe
  or analyze experiments.

Roadmap: `docs/roadmap.md` · Architecture: `docs/architecture.md` · Decisions: `apps/docs/docs/adr/`
· Run file format: `docs/run-format.md`

There is **no backend besides the leaderboard**. Do not introduce servers, message brokers,
Docker services, accounts, or social features — those were explicitly removed from scope.

---

## 2. Repository layout

```
engine/              Rust crate — pure, deterministic simulation core. No Tauri, no I/O,
                     no rendering, no networking. Compiled natively (desktop) and to WASM (web).
apps/
  desktop/           Tauri v2 — React + TS frontend, Rust backend (src-tauri/) that uses `engine`,
                     run files, SQLite gallery index, batch runs, export
  web/               Next.js — leaderboard, challenge pages, landing page, verification API route
  docs/              Docusaurus — docs, ADRs, devlog (blog) → GitHub Pages
packages/
  ui/                Shared React components (charts, renderer, inspectors) for desktop + web
  types/             TS types generated from Rust (do not edit by hand)
.github/             CI/CD workflows, issue + PR templates, CODEOWNERS
```

Area-specific rules live in nested `CLAUDE.md` files (e.g. `engine/CLAUDE.md`). Follow them when
working in that area.

---

## 3. Tech stack

| Concern | Choice |
|---|---|
| Engine | Rust, seeded RNG (`rand_chacha`), fixed timestep, numeric strategy per ADR-0002 |
| Desktop | Tauri v2, React, TypeScript, PixiJS (world view), ECharts/uPlot (charts) |
| Desktop storage | Versioned run files (serde) + SQLite gallery index |
| Batch runs | `rayon` — parallel **across** runs only, each run single-threaded |
| Rust → TS types | Generated (e.g. `tauri-specta` / `ts-rs`) into `packages/types` |
| Web / leaderboard | Next.js on Vercel, API routes, engine via `wasm-pack` |
| Leaderboard DB | One free hosted database (chosen in an ADR at Phase 4 kickoff) |
| Monorepo | Cargo workspace + pnpm workspaces + Turborepo |
| Docs | Docusaurus on GitHub Pages |
| Distribution | GitHub Releases + Tauri updater |

Do not introduce new frameworks, languages, services or major dependencies without an ADR
approved by the team. Ask first.

---

## 4. Commands

```bash
# setup
pnpm install

# develop
cargo tauri dev                     # desktop app
pnpm dev --filter web               # leaderboard / website
pnpm dev --filter docs              # docs site

# quality — run the relevant ones before every commit
cargo fmt --all && cargo clippy --all-targets -- -D warnings
cargo test --workspace
pnpm lint && pnpm typecheck && pnpm test
pnpm format

# engine
cargo test -p engine determinism    # determinism tests (must pass for any engine change)
cargo bench -p engine               # performance benchmarks
pnpm build:wasm                     # build engine.wasm for the web app

# generated types
pnpm types:generate                 # regenerate packages/types from Rust
```

These commands describe the planned setup. If one is wrong or missing, fix this file in the same PR.

---

## 5. Hard rules — NEVER

- **NEVER** push to `main` or `dev` directly. All changes go through PRs.
- **NEVER** merge a PR yourself, approve a PR, or bypass branch protection. You may enable
  auto-merge (`gh pr merge --auto --squash`) on PRs you opened; a human approval is still required.
- **NEVER** force-push to any branch except your own feature branch, and not after review has
  started unless the developer asks.
- **NEVER** commit secrets, tokens, `.env` files or credentials. Document new variables in
  `.env.example` (name + description, no values).
- **NEVER** touch production (Vercel project settings, the leaderboard database), GitHub
  settings, rulesets or secrets.
- **NEVER** introduce non-determinism into `engine/` (see §7).
- **NEVER** change the run file format without bumping `format_version` and adding a migration
  plus a fixture test (see §8).
- **NEVER** let the leaderboard trust client-provided scores or results. The server always
  re-simulates (see §9).
- **NEVER** disable, skip or weaken tests, lints or CI checks to make something pass.
- **NEVER** edit generated code by hand (`packages/types/`, `*.generated.*`). Change the Rust
  source and regenerate.
- **NEVER** add servers, brokers, accounts or social features — out of scope by team decision.
- **NEVER** start work without an issue. If none exists, ask the developer to create one or offer
  to draft it.

---

## 6. Workflow for every task

### 6.1 Start
1. Read the issue: `gh issue view <N> --comments`. Read linked ADRs/docs and the relevant
   roadmap phase.
2. If acceptance criteria are unclear or the task conflicts with an ADR or the roadmap, **stop
   and ask**.
3. Assign and mark in progress: `gh issue edit <N> --add-assignee @me`, then set Status to
   **In Progress** on the GitHub Project.
4. For anything beyond a small change, propose a plan first and wait for approval.

### 6.2 Branch
- `dev` is the default branch. Always branch from an up-to-date `dev`:
  `git fetch origin && git switch -c <type>/<N>-<short-kebab-name> origin/dev`
- Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`
- `hotfix/<N>-...` branches from `main` — only when the developer explicitly asks.
- One issue per branch. Stay current with `git rebase origin/dev`; never merge `dev` into it.

### 6.3 Commit
Conventional Commits, imperative mood, ≤72 char subject:

```
<type>(<scope>): <subject>

<optional body: what and why, not how>

Refs #<N>
```

Scopes: `engine`, `desktop`, `web`, `ui`, `types`, `docs`, `ci`, `release`.
One logical change per commit. Commit early and often.

### 6.4 Pull request
- Target `dev` (or `main` only for hotfixes/releases).
- Title follows Conventional Commits — it becomes the squash commit.
- Fill in `.github/pull_request_template.md` completely: summary, motivation, how to test,
  screenshots/GIFs for UI changes, risk notes, `Closes #<N>`.
- **Size limit: ~400 changed lines** (excluding generated files and lockfiles). If larger, split
  into stacked PRs and say so.
- Open as **draft** if not ready.
- `gh pr create --base dev --fill-first`, edit the body to match the template, then
  `gh pr merge --auto --squash`, and report the PR link to the developer.

### 6.5 Before marking ready
- [ ] Formatter, linter, typecheck and tests pass for every touched area
- [ ] Determinism tests pass if `engine/` changed; `ENGINE_VERSION` bumped if outcomes changed
- [ ] Benchmarks show no significant regression if hot paths changed
- [ ] Run-format fixtures still load if anything near serialization changed
- [ ] Generated types regenerated if Rust types exposed to TS changed
- [ ] New logic has tests; bug fixes have a regression test
- [ ] Docs / run-format doc / READMEs / `.env.example` updated where affected
- [ ] No debug output, commented-out code or unrelated changes
- [ ] PR description calls out risky parts so reviewers know where to look

### 6.6 Reviews and CI
- If CI fails, read the logs (`gh pr checks`, `gh run view --log-failed`), fix the root cause,
  push a new commit. Do not re-run hoping it passes.
- Address review comments with new commits, then reply on each thread summarizing the change.
  Don't resolve threads — the reviewer does.
- If you disagree with a review comment, explain why and let the humans decide.

---

## 7. Engine rules (`engine/`) — determinism is sacred

- All randomness comes from the world's seeded RNG. No `thread_rng`, no `rand::random`, no OS
  entropy. Sub-systems derive their own RNG streams from the world seed deterministically.
- No wall-clock time (`SystemTime`, `Instant`) in simulation logic. Time = tick count.
  Day/night and seasons are functions of the tick.
- Fixed timestep, independent of frame rate or real elapsed time.
- No order-dependent iteration over `HashMap`/`HashSet`. Use `BTreeMap`, `IndexMap`, or sort.
- **No threading inside a single run.** Parallelism only across independent runs (batch).
- Follow the numeric strategy in **ADR-0002** (fixed-point or strict floats). Never use
  platform-dependent math (`sin`, `exp`, `powf`, …) from `std` in simulation paths unless the
  ADR allows it — use the engine's math module.
- Interventions are applied only at tick boundaries, from the run's tick-indexed input list.
- Every behavior change that alters outcomes for the same inputs **must bump `ENGINE_VERSION`**
  and be noted in the PR.
- The engine is a pure library: no I/O, networking, rendering, logging side effects or Tauri code.
- Genome and brain are separate: brains implement the `Brain` trait. v1 is rule-based;
  neural-network brains (Phase 6) plug into the same trait. Don't couple genome to a brain impl.
- Speciation, biomes, seasons etc. are deterministic systems like everything else — no
  shortcuts.
- Performance targets (see roadmap §5.3): avoid allocations in the tick loop, use spatial
  partitioning, add/update a benchmark for hot-path changes.
- Every run produces full statistics; anything shown in a chart must be exportable.

---

## 8. Run file format

- Spec: `docs/run-format.md`. A run file contains: `format_version`, `engine_version`, seed,
  world config, rules, creature designs, scheduled events, tick-indexed interventions, experiment
  notes, metadata.
- Replays are **re-simulation** — never store full state per tick. Optional snapshot caches are
  derived data and may be deleted/rebuilt.
- **Any change to the format:**
  1. bump `format_version`
  2. add a migration from the previous version
  3. add a fixture file for the new version in `engine/tests/fixtures/run-files/`
  4. keep all older fixtures loading (CI tests every fixture)
  5. update `docs/run-format.md`
- Loading never panics on bad input: return clear errors.
- If a run's `engine_version` differs from the current engine, follow the documented policy
  (replay with compatible engine or mark as "re-simulated with vX"). Never silently change results.

---

## 9. Leaderboard (`apps/web`)

- The client submits a **signed run file**. The server:
  1. validates schema, size and challenge ID
  2. verifies the signature against the submitter's public key
  3. re-runs the run with `engine.wasm` up to the challenge's **fixed tick limit**
  4. computes the score server-side and stores it
- Never accept or store a client-computed score as truth.
- Challenges are pinned to an `engine_version`. The server must be able to verify runs for every
  active challenge's engine version.
- Verification must stay well within the Vercel free-plan function limits — keep tick limits and
  world sizes bounded; benchmark verification time.
- Identity: display name + public key only. No email, no passwords, no tracking.
- Store the minimum: display name, public key, run file, score, timestamps.
- Display names and run titles go through the offensive-name filter. Rate-limit per key and IP.
- Admin actions (hide entry) require auth and are never exposed to normal users.
- Privacy note must stay accurate whenever stored data changes.

---

## 10. Code standards

### General
- Match the existing style; formatters are the authority.
- Small, focused functions; clear names over comments; comments explain *why*.
- No dead or commented-out code. `TODO` must reference an issue: `// TODO(#57): ...`
- Handle errors explicitly. No swallowed errors.
- Don't add dependencies casually — justify in the PR, prefer well-maintained, widely used ones.

### Rust
- `cargo fmt`, `clippy -D warnings` clean.
- No `unwrap()`/`expect()` outside tests unless provably infallible (comment why).
- Errors via `thiserror` in libraries, `anyhow` only in binaries/app glue.
- Public items in `engine` have doc comments.
- Tauri commands are thin: validate input, call engine/app logic, return typed results.

### TypeScript
- `strict` mode. No `any` (use `unknown` + narrowing). No `@ts-ignore` without an issue reference.
- Types shared with Rust come from `packages/types` (generated) — never redefine by hand.
- React: function components + hooks. Shared UI goes into `packages/ui`.
- Next.js: server components by default; client components only when needed.
- Validate all API input at the boundary.

### Data
- SQLite (desktop) and the leaderboard DB change only via migrations; migrations are
  forward-only and reviewed as high-risk.
- Never build SQL by string concatenation with user input.
- The SQLite gallery is an index; run files are the source of truth.

---

## 11. Testing

- Engine changes require tests. Determinism tests: same run file ⇒ identical state hash after N
  ticks.
- **Cross-platform determinism CI** compares hashes across Windows, macOS, Linux and WASM — it
  must always be green.
- Run-format fixture tests: every historical version loads and migrates correctly.
- Benchmarks run in CI; investigate regressions before merging.
- TS: Vitest for units; Playwright for key desktop/web flows where feasible.
- Bug fix ⇒ regression test that fails without the fix.
- Flaky tests: fix or quarantine with an issue reference — never retry-until-green.
- Tests must not depend on network access or real cloud services.

---

## 12. Documentation

- A change is not done until its docs are updated.
- **ADRs** (`apps/docs/docs/adr/NNNN-title.md`): propose one for any architectural decision.
  Format: Context, Decision, Consequences, Status. Draft it; humans decide.
- **Run format doc** stays in sync with the code.
- **User docs** for user-facing features (designer, editors, events, batch runs, export,
  challenges), including the science background where relevant.
- **READMEs:** every app/crate explains what it is, how to run it, how to test it.
- **Devlog** (`apps/docs/blog/`): you may collect facts and links (merged PRs, closed issues,
  screenshots). Humans write the post in their own voice.
- Keep this `CLAUDE.md` accurate; propose edits when you find something wrong or missing.

---

## 13. Notion (team notes)

The team's Notion workspace has a **Primordia** hub page (teamspace "General") with four
databases. Use the Notion MCP tools (configured in `.mcp.json`) to read and write them.

| Database | Use for |
|---|---|
| **Agent Notes** | Session logs, handovers, research findings, bug investigations, decision drafts |
| **Meeting Notes** | Check-ins, demos, retros, planning |
| **Research & References** | Papers, articles, libraries with a short summary |
| **Playtest Log** | Observations from running experiments (seed, engine version, verdict) |

Rules:
- **Repo = source of truth, Notion = working notes.** Anything describing how the code works or
  a decision the team made goes into the repo (docs, ADRs). Notion holds notes, research and
  observations.
- Save into the databases, never as loose pages. Fetch the database first and use its exact
  property names.
- Agent Notes: always set Type, Area, Written by = Claude, Author = the developer you work for,
  and Issue / PR when there is one. Status starts as Draft.
- Write a **Handover** note when a session ends mid-task: what's done, what's next, open
  questions, branch name.
- Before starting an issue, search Agent Notes for earlier notes on it.
- Never store secrets, tokens or personal data in Notion.
- Never delete or rewrite other people's pages — comment or add a new note instead.
- A "Decision draft" only becomes a decision as an ADR in the repo, approved by the team.
- Actionable playtest findings become GitHub issues; link the issue back in the Playtest Log.

---

## 14. GitHub Projects

- Status: Backlog → Ready → In Progress → In Review → Done.
- Fields: Area (engine, desktop, web, docs, infra), Size (S/M/L), Priority (P0–P2), Iteration,
  Milestone (v0.1 First Life … v1.0 Launch, v2.0 Brains).
- When creating issues: use the templates; include goal, acceptance criteria, area, size, links
  to roadmap phase / ADRs / docs; add to the project.
- Useful commands:
  ```bash
  gh issue list --assignee @me --state open
  gh issue view <N> --comments
  gh project item-list <project-number> --owner <org>
  gh project field-list <project-number> --owner <org>
  gh project item-edit --id <item-id> --project-id <project-id> --field-id <field-id> --single-select-option-id <option-id>
  ```
- Never close issues or change priorities/milestones on your own — suggest it.

---

## 15. When to stop and ask

Stop and ask the developer before:
- Changing architecture, adding a dependency, service or technology
- Any breaking change (run format, engine outcomes, leaderboard API, DB schema)
- Anything touching leaderboard verification, signing, identity or stored user data
- Touching another area's code in a non-trivial way (see `CODEOWNERS`)
- Deleting files or large amounts of code
- Anything involving secrets, infra, CI permissions or deployments
- When the issue is ambiguous or the requested approach seems wrong — say so and explain

Report honestly: what you did, what you verified, what failed, what you skipped.

---

## 16. Definition of done

- [ ] Linked issue's acceptance criteria met
- [ ] PR against the right base, template filled, `Closes #N`, auto-merge enabled
- [ ] CI green (incl. cross-platform determinism, fixtures, benchmarks)
- [ ] Tests added/updated
- [ ] Docs / run-format doc / `.env.example` updated where relevant
- [ ] Risky parts called out for the reviewer
- [ ] Developer informed with PR link and a short summary

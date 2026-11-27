# DEV.md — Team Handbook

How we work on **Primordia**. This is for us humans.
- `CLAUDE.md` — Claude Code's instructions (same rules, written for Claude)
- `HOW-WE-WORK.md` — the short, informal version of this file. Read that first.
- `docs/roadmap.md` — what we're building and when

If you change a rule here, check `CLAUDE.md` too. Any rule can change — by team agreement and a
PR to this file.

---

## Contents

1. [Getting set up](#1-getting-set-up)
2. [How we work — the big picture](#2-how-we-work--the-big-picture)
3. [Daily workflow](#3-daily-workflow)
4. [Branches](#4-branches)
5. [Commits](#5-commits)
6. [Pull requests](#6-pull-requests)
7. [Code review](#7-code-review)
8. [CI/CD](#8-cicd)
9. [Branch protection & repo settings](#9-branch-protection--repo-settings)
10. [Releases](#10-releases)
11. [GitHub Projects & issues](#11-github-projects--issues)
12. [Working with Claude Code](#12-working-with-claude-code)
13. [Engine, determinism & run files](#13-engine-determinism--run-files)
14. [Leaderboard](#14-leaderboard)
15. [Secrets & config](#15-secrets--config)
16. [Notion](#16-notion)
17. [Documentation & devlog](#17-documentation--devlog)
18. [Definition of done](#18-definition-of-done)
19. [Team habits](#19-team-habits)
20. [Who owns what](#20-who-owns-what)

---

## 1. Getting set up

### Accounts
- GitHub (member of our org, **2FA enabled**)
- Claude Code
- From Phase 4 only (leaderboard owner + backup): Vercel team, leaderboard database

That's it — no cloud servers, no Kafka, no Docker.

### Tools to install
| Tool | Why |
|---|---|
| Git + GitHub CLI (`gh`) | PRs, issues, project board — used by you and Claude |
| Rust (stable, via rustup) | engine, desktop backend |
| `wasm-pack` | engine → WASM for the leaderboard |
| Tauri v2 prerequisites | OS-specific (see Tauri docs) + `cargo install tauri-cli` |
| Node.js (LTS) + pnpm | desktop UI, website, docs |
| Claude Code | our AI pair programmer |

### First-time setup
```bash
git clone <repo-url> && cd Primordia
gh auth login
gh auth refresh -s project      # lets gh (and Claude) edit the project board
pnpm install
cargo tauri dev                 # desktop app should start
cargo test --workspace && pnpm test
```

A fresh clone that doesn't work with these steps is a bug — open an issue.

### Editor
- **Format on save** (rustfmt, Prettier).
- Recommended: rust-analyzer, ESLint, Prettier, Even Better TOML.

---

## 2. How we work — the big picture

```
Plan together  →  Issues on the board  →  Everyone picks issues  →  Claude builds on a branch
     ↑                                                                        ↓
  Retro & re-plan  ←  Demo  ←  Release  ←  Auto-merge  ←  Human review  ←  PR + CI
```

- **Planning** together at each phase kickoff, with Claude helping to break work into issues.
- **Execution** separately: everyone picks issues and works in their own Claude Code session.
- **Quality** comes from three layers:
  1. 🤖 **Automation** — branch protection, CI, hooks (can't be skipped)
  2. 🧠 **Claude following `CLAUDE.md`** — conventions, tests, docs (mostly reliable)
  3. 👤 **Us** — decisions, reviews, playtesting, accountability (irreplaceable)

---

## 3. Daily workflow

1. **Pick** an issue from **Ready**. Assign yourself. Max 2 in progress.
2. **Start Claude** in the repo: *"Work on issue #42. Propose a plan first."*
3. **Approve or fix the plan.** Use plan mode for anything non-trivial.
4. **Let Claude build — stay involved.** Run the app, look at the simulation, check direction.
5. **Read your whole diff** before requesting review. You own every line.
6. **Claude opens the PR**: template filled, `Closes #42`, auto-merge on.
7. **Review** is requested from the code owner automatically. Ping chat if urgent.
8. **Fix feedback** → approval → GitHub merges → branch deleted → issue Done.
9. **Do your own reviews** — check the queue daily.

---

## 4. Branches

| Branch | Purpose | From | Into |
|---|---|---|---|
| `main` | Released code | — | — |
| `dev` | Integration of finished work | `main` | `main` (release PR) |
| `feat/<N>-name` | New feature | `dev` | `dev` |
| `fix/<N>-name` | Bug fix | `dev` | `dev` |
| `chore/` `docs/` `refactor/` `test/` `perf/` `ci/` | Other work | `dev` | `dev` |
| `hotfix/<N>-name` | Urgent fix for a release | `main` | `main` **and** `dev` |

- Every branch belongs to an issue. No issue → no branch.
- Short-lived: merge within days. Big features = several small PRs.
- **Rebase** on `dev`; don't merge `dev` into your branch.
- Branches auto-delete after merge.
- Force-push only your own branch, and not after review started (unless agreed).

---

## 5. Commits

**Conventional Commits**, imperative, subject ≤ 72 chars:

```
feat(engine): add seasonal food regrowth
fix(desktop): prevent crash when world has 0 creatures
docs(adr): choose fixed-point arithmetic
perf(engine): spatial hash for neighbor lookup
```

| Type | Use for |
|---|---|
| `feat` | new user-facing functionality |
| `fix` | bug fix |
| `docs` | documentation only |
| `refactor` | no behavior change |
| `test` | tests |
| `perf` | performance |
| `chore` | tooling, deps |
| `ci` | CI/CD |

Scopes: `engine`, `desktop`, `web`, `ui`, `types`, `docs`, `ci`, `release`.

PRs are **squash-merged** → the **PR title** is the commit on `dev` and feeds the changelog.

---

## 6. Pull requests

- **One issue per PR**, `Closes #N`.
- **< ~400 changed lines** (excluding generated files/lockfiles). Split otherwise.
- **Template filled**: what, why, how to test, screenshots/GIFs, risks.
- **Draft early** if you want feedback on direction.
- **Never self-merge, never approve your own PR.** Auto-merge does it after approval + CI.
- **Call out risky parts** so reviewers know where to look.
- Reviewer resolves threads, not the author.
- PR idle for 5 days → discussed at the next check-in.

---

## 7. Code review

### Two different reviews
- **Author self-review — every line.** Claude wrote it, you asked for it, you own it.
- **Reviewer — approach and risk.** Right approach? What breaks? Tested? CI already did the
  formatting/types/tests part.

### Depth by risk
| What changed | Depth |
|---|---|
| Engine logic, determinism, numerics, speciation | 🔴 Careful line-by-line |
| Run file format, migrations | 🔴 Careful — old runs must keep working |
| Leaderboard verification, signing, stored data | 🔴 Careful — this is the trust model |
| Batch runs / threading | 🟠 Check no shared state leaks into a run |
| CI, release pipeline | 🟠 No secrets exposed, no permissions widened |
| Desktop app logic, Tauri commands | 🟠 Logic + edge cases |
| UI components, charts | 🟢 Run it / look at it, skim code |
| Tests | 🟢 Do they test the right thing? |
| Docs, devlog | 🟢 Skim |

### Review fast
1. Read description + tests first.
2. Read the AI review comments — they point at suspicious spots.
3. Ask Claude: *"Summarize PR #N, list risky parts, explain determinism impact."* Then
   **verify** those spots yourself.
4. UI change? Pull the branch and run it, or check the GIF in the PR.
5. `nit:` for non-blocking comments.

### Etiquette
- Respond within **24–48 h**.
- Comment on the code, not the person.
- Approve when it's good and safe — not only when it's how you'd write it.
- "Request changes" only for real problems.

---

## 8. CI/CD

### CI — every PR
| Check | Tools | Blocks merge |
|---|---|---|
| Formatting | `rustfmt --check`, `prettier --check` | ✅ |
| Linting | `clippy -D warnings`, `eslint` | ✅ |
| Type check | `tsc --noEmit` | ✅ |
| Unit tests | `cargo test`, `vitest` | ✅ |
| **Cross-platform determinism** | same run files on Win/macOS/Linux/WASM ⇒ identical hashes | ✅ |
| **Run-format fixtures** | every historical format version loads + migrates | ✅ |
| Generated types up to date | regenerate + diff must be empty | ✅ |
| Benchmarks | `cargo bench` vs. baseline | ⚠️ alert on regression |
| Builds | Tauri (Linux on PRs), WASM, web, docs | ✅ |
| Security | Dependabot, `cargo audit`, secret scanning | ⚠️ alerts |
| AI review | Claude GitHub Action | ❌ advisory |

- Path filters + Turborepo → only affected parts run.
- Caching for cargo, pnpm, Turborepo.
- **Red `dev` = stop and fix.** It's more important than new features.
- **No retry-until-green.**

### CD
| Trigger | What happens |
|---|---|
| PR touching `apps/web` | Vercel preview deploy, link on PR (from Phase 4) |
| Merge to `main` | Web → production (Vercel), docs → GitHub Pages |
| Tag `v*.*.*` | Desktop builds for Win/macOS/Linux → GitHub Release → Tauri auto-updater |

Rollback: Vercel instant rollback; desktop users can install the previous release.

---

## 9. Branch protection & repo settings

Set once via **GitHub rulesets** by the infra/release owner. No bypass for anyone — including
admins and Claude's tokens.

Rulesets are stored in `.github/rulesets/*.json` and applied with `scripts/setup-github.sh`.
`dev` is the **default branch**, so PRs target it automatically.

**`main` and `dev`:**
- ✅ PR required
- ✅ **1 approval on `dev`**, **1 approval + release checklist on `main`**
- ✅ Dismiss stale approvals on new commits
- ✅ CODEOWNERS review required
- ✅ All status checks must pass
- ✅ Branch must be up to date
- ✅ Conversations resolved
- ✅ `dev`: squash merge only, linear history
- ✅ `main`: merge commits for release PRs (`dev → main`), squash for hotfixes — so `dev` and `main` never diverge
- ✅ No force-push, no deletion

**Repo:**
- ✅ Auto-delete head branches, allow auto-merge
- ✅ Secret scanning + push protection, Dependabot
- ✅ **Public repo** (free rulesets + unlimited Actions minutes)

> Claude acts with *your* GitHub identity — a PR Claude opens is *your* PR. You can't approve
> it; a teammate must. That's the point.

---

## 10. Releases

1. **release-please** keeps a release PR with version bump + changelog.
2. At the end of a phase/milestone: open the `dev → main` PR.
3. **Release checklist:**
   - [ ] Demo flow works on all 3 OSes: design creature → build world → release → run →
         intervene → save → replay → export
   - [ ] (Phase 4+) Submit a run → server score matches local score
   - [ ] Old run-file fixtures still open
   - [ ] `ENGINE_VERSION` bumped if outcomes changed; active challenges still verifiable
   - [ ] Changelog makes sense
4. Merge the release PR with a **merge commit** (not squash) → web/docs deploy. Merge release-please PR → tag → desktop builds → GitHub Release.
5. Announce in chat + devlog post.

**Versioning:** SemVer, `0.x` until launch. Engine has its own `ENGINE_VERSION`; run files have
their own `format_version`.

**Milestones:** `v0.1 First Life` · `v0.2 The Lab` · `v0.3 Local Gallery` ·
`v0.4 Challenges & Leaderboard` · `v1.0 Launch` · `v2.0 Brains`

---

## 11. GitHub Projects & issues

### Board
**Backlog → Ready → In Progress → In Review → Done**

| Field | Values |
|---|---|
| Area | engine, desktop, web, docs, infra |
| Size | S (≤ half day), M (1–2 days), L (split it!) |
| Priority | P0 must / P1 should / P2 could |
| Iteration | sprint |
| Milestone | release |

### Rules
- Everything is an issue (templates: feature, bug, chore).
- **Ready** = goal, acceptance criteria, size, area, links to roadmap/ADRs/docs.
- Assign yourself before starting. One person per issue. Max 2 in progress.
- PR opened → In Review, merged → Done (automations).
- L issues get split before Ready.

### A good issue
```markdown
## Goal
Food regrows depending on biome and season.

## Acceptance criteria
- [ ] Each biome has a base regrowth rate
- [ ] Regrowth multiplied by a seasonal factor (season length in ticks, configurable)
- [ ] Covered by determinism tests; ENGINE_VERSION bumped
- [ ] Editable in the rules editor
- [ ] Exposed in stats export

## Context
Roadmap Phase 2 · ADR-0002 (numerics) · docs/architecture/world.md
Area: engine (+ small desktop change)
```

### Planning
- **Phase kickoff:** plan that phase in detail with Claude. Later phases stay rough.
- **Sprints:** 1–2 weeks.
- **Phase 2 is big** → mid-phase review to re-check scope.
- **End of Phase 3:** cut-line decision (is Phase 4 in v1.0?).

---

## 12. Working with Claude Code

### The deal
Claude writes most of the code. **We own the decisions, reviews and quality.** "Claude did it"
is never an excuse.

### Shared setup (committed)
| File | Purpose |
|---|---|
| `CLAUDE.md` | Project-wide rules |
| `engine/CLAUDE.md`, `apps/*/CLAUDE.md` | Area-specific rules |
| `.claude/settings.json` | Shared permissions + hooks (format/lint after edits) |
| `.claude/skills/` | Shared commands, e.g. `/write-adr`, `/new-run-format-version`, `/new-challenge` |

Personal preferences: `CLAUDE.local.md` (gitignored) or `~/.claude/CLAUDE.md`.

### Rules
1. **Decide first, then prompt.** Architecture → ADR/issue first.
2. **Plan mode** for anything non-trivial. Push back on bad plans.
3. **One issue per session.**
4. **Understand every line** before requesting review.
5. **AI code follows the same rules**: size, CI, review.
6. **Commit often** so you can roll back.
7. **Claude repeats a mistake → add a rule to `CLAUDE.md`** via PR.
8. **Watch for hallucinations**: fake APIs, outdated crate/Tauri/Next.js usage.
9. **Never** let Claude handle secrets, production or GitHub settings.
10. **The engine owner understands the engine without AI.** Pair on it sometimes.

### Useful prompts
- *"Work on issue #42. Propose a plan first."*
- *"Summarize PR #57, list risky parts, explain the determinism impact."*
- *"CI failed on my PR — find the root cause and fix it."*
- *"Address the review comments on PR #57."*
- *"Draft an ADR: fixed-point vs strict floats for the engine."*
- *"List what I merged this sprint with links, as notes for my devlog."*

### Where Claude is weak (steer it)
- Whether the simulation is *interesting* — that's playtesting, that's us
- Cross-platform numeric determinism
- Real performance work (profile, don't guess)
- UX and visual taste

---

## 13. Engine, determinism & run files

**Same run file + same engine version ⇒ identical result on every platform.** Everything
depends on this: replays, remixes, batch comparisons, leaderboard verification.

- Only the world's seeded RNG. Time = ticks. Fixed timestep.
- No order-dependent hash map iteration.
- No threads inside a run; batch runs parallelize across runs.
- Numerics per ADR-0002 — no platform-dependent math in simulation code.
- Interventions are tick-indexed inputs in the run file.
- Outcome changes bump `ENGINE_VERSION`.
- Engine = pure library (no I/O, rendering, Tauri).
- Genome and `Brain` are separate (Phase 6 neural nets plug in).

**Run files:** versioned (`format_version`). Any format change = version bump + migration +
fixture + doc update. Old files must always open. Spec in `docs/run-format.md`.

**Performance targets** (provisional, confirmed after Phase 1): 2,000 creatures at 60 fps
rendered; 10,000 creatures at ≥ 200 ticks/s headless; batch runs scale with cores.

Engine and run-format PRs are always 🔴 reviews with the engine owner.

---

## 14. Leaderboard

The only online part (Phase 4). Small, but it's where trust and user data live.

- Client submits a **signed run file**, never a score.
- Server re-simulates with `engine.wasm` up to the challenge's tick limit, computes the score.
- Challenges are pinned to an engine version.
- Identity = display name + app-generated key. No email, no passwords.
- Store the minimum. Privacy note stays accurate.
- Offensive-name filter, rate limiting, admin hide.
- Verification must fit the Vercel free plan limits with margin.

---

## 15. Secrets & config

- Few secrets exist (leaderboard DB, Vercel, release signing if any) — **owner + backup only**.
- **Never commit secrets.** `.env` gitignored; `.env.example` lists variables without values.
- Secrets live only in GitHub Actions secrets and Vercel env vars.
- Never paste secrets into Claude, chat, issues or PRs.
- **Leaked one?** Rotate immediately, then tell the team. Deleting the commit isn't enough.

---

## 16. Notion

The **Primordia** hub in our Notion workspace (teamspace "General") holds working notes. The
repo stays the source of truth for code, docs and decisions.

| Database | For |
|---|---|
| Agent Notes | Claude session logs, handovers, research, bug investigations, decision drafts |
| Meeting Notes | Check-ins, demos, retros, planning |
| Research & References | Papers, articles, libraries |
| Playtest Log | What you saw when running experiments — boring, broken, surprising |

- Claude connects via `.mcp.json` (Notion MCP). The first time, Claude Code asks you to sign in
  to Notion — use your own account. Cloud sessions use the Notion connector on claude.ai.
- Ask Claude to *"write a handover note"* when you stop mid-task, and to *"check Agent Notes
  for #42"* when you pick something up.
- Decisions drafted in Notion only count once they're an ADR in the repo.
- No secrets or personal data in Notion.

---

## 17. Documentation & devlog

Docusaurus in `apps/docs` → GitHub Pages.

| Section | Contents |
|---|---|
| User guide | Designer, world/rules editors, events, batch runs, export, gallery, challenges |
| Science background | How evolution, genetics, speciation, biomes are modeled |
| `docs/run-format.md` | Run file spec + examples |
| Developer docs | Architecture, setup, engine internals |
| `docs/adr/` | One page per decision |
| `blog/` | Devlog — at least one post per sprint, rotating author |

Devlog: written by a human in your own voice. Claude may collect facts/links. Link issues, PRs,
ADRs. Show GIFs of evolving worlds and charts. Honest > polished.

---

## 18. Definition of done

- [ ] Acceptance criteria met
- [ ] Merged into `dev` via approved PR
- [ ] CI green (incl. cross-platform determinism + fixtures)
- [ ] Tests added/updated
- [ ] Docs / run-format doc / README updated where relevant
- [ ] Verified by running the app (not just tests)
- [ ] Issue closed, board up to date

---

## 19. Team habits

- **Check-ins** twice a week: done / next / blocked.
- **Sprint end:** demo (everyone shows something) + retro (keep / stop / try).
- **Playtest every week.** Run experiments, watch them, file issues for what's boring or broken.
- **Communicate early.** Blocked, behind, changing direction → say it.
- **Big changes discussed first** — ADR or quick call.
- **Red `dev` = stop and fix.**
- **Reviews are part of the work.**

---

## 20. Who owns what

Fill in once the team is settled. Mirrors `.github/CODEOWNERS`.

| Area | Owner | Backup |
|---|---|---|
| Engine (`engine/`) — simulation, determinism, performance, WASM | | |
| Desktop (`apps/desktop/`, `packages/ui`) — designer, editors, analysis, gallery | | |
| Leaderboard + docs (`apps/web/`, `apps/docs/`) — site, verification, DB, docs | | |
| Release & CI (`.github/`, `scripts/`) | | |
| Devlog rotation | everyone | |

More than three people? Split Desktop into *Lab UI* and *Visualization & analysis*.

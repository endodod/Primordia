#!/usr/bin/env python3
"""Create the roadmap's labels, milestones and issues on GitHub (idempotent).

Usage:  python3 scripts/seed-issues.py [--repo endodod/Primordia] [--dry-run]
Needs:  gh CLI, authenticated. Issues whose title already exists are skipped.
Source: docs/roadmap.md — keep the two in sync when re-planning.
"""

import argparse
import json
import subprocess
import sys

LABELS = {
    "area: engine": ("8957e5", "Simulation engine"),
    "area: desktop": ("1f6feb", "Desktop app"),
    "area: web": ("2ea043", "Website / leaderboard"),
    "area: docs": ("d29922", "Docs site, ADRs, devlog"),
    "area: infra": ("6e7781", "CI, release, repo"),
    "type: feature": ("0e8a16", "New functionality"),
    "type: bug": ("d73a4a", "Something is broken"),
    "type: chore": ("c5def5", "Tooling, refactor, deps"),
    "type: decision": ("f9d0c4", "Needs an ADR / team decision"),
    "P0": ("b60205", "Must, now"),
    "P1": ("fbca04", "Should"),
    "P2": ("c2e0c6", "Could"),
    "size: S": ("ededed", "Half a day or less"),
    "size: M": ("bfd4f2", "1-2 days"),
    "size: L": ("5319e7", "Too big - split before Ready"),
    "good first issue": ("7057ff", "Small, self-contained"),
    "determinism": ("e99695", "Affects simulation outcomes"),
}

MILESTONES = {
    "v0.0 Foundation": "Phase 0 - repo, CI, a dot moves",
    "v0.1 First Life": "Phase 1 - creatures evolve deterministically",
    "v0.2 The Lab": "Phase 2 - designer, biomes, rules, events, batch runs",
    "v0.3 Local Gallery": "Phase 3 - gallery, replays, remix",
    "v0.4 Challenges & Leaderboard": "Phase 4 - verified online leaderboard",
    "v1.0 Launch": "Phase 5 - installers, docs, beta",
    "v2.0 Brains": "Phase 6 - neural-network brains",
}

# (milestone, title, area, type, priority, size, goal, [criteria], context)
P0, P1, P2 = "P0", "P1", "P2"
ISSUES = [
    # ---------------- Phase 0 ----------------
    ("v0.0 Foundation", "Apply rulesets, repo settings and project board", "infra", "chore", P0, "S",
     "Protect main/dev and create the GitHub Project, which needs admin rights outside Claude sessions.",
     ["Run `scripts/setup-github.sh` as repo admin", "Rulesets protect-main and protect-dev active",
      "dev is the default branch; auto-merge and branch auto-delete enabled",
      "Project board has Status: Backlog/Ready/In Progress/In Review/Done + Iteration field",
      "Run `python3 scripts/sync-project.py` to add all issues to the board"],
     "DEV.md §9, §11"),
    ("v0.0 Foundation", "Assign area owners and fill CODEOWNERS", "infra", "chore", P0, "S",
     "Every area has an owner and a backup so reviews are routed automatically.",
     ["Owners/backups filled in DEV.md §20", "`.github/CODEOWNERS` updated",
      "`require_code_owner_review` set to true in rulesets and re-applied"],
     "Roadmap §10"),
    ("v0.0 Foundation", "Choose a license", "docs", "decision", P0, "S",
     "Decide MIT vs Apache-2.0 (or dual) and add it to the repo.",
     ["ADR written", "`LICENSE` file added", "`license` set in Cargo.toml and package.json files",
      "README updated"],
     "Roadmap §5.6, §12"),
    ("v0.0 Foundation", "Add CONTRIBUTING.md and CODE_OF_CONDUCT.md", "docs", "chore", P1, "S",
     "Public-facing contribution docs derived from DEV.md.",
     ["CONTRIBUTING.md links to HOW-WE-WORK.md and DEV.md", "Code of conduct added (e.g. Contributor Covenant)"],
     "Roadmap §5.6"),
    ("v0.0 Foundation", "Verify fresh-clone setup on Windows, macOS and Linux", "infra", "chore", P0, "M",
     "Everyone can clone and run the desktop app with `pnpm install` + `cargo tauri dev`.",
     ["Each team member confirms setup on their OS", "Missing prerequisites documented in DEV.md §1",
      "Any fixes merged"],
     "Roadmap Phase 0 DoD"),
    ("v0.0 Foundation", "Shared Claude Code setup: hooks and skills", "infra", "chore", P1, "M",
     "Claude formats/lints automatically and the team shares common commands.",
     ["Hook in `.claude/settings.json` formats edited files (rustfmt / prettier)",
      "Skills in `.claude/skills/`: `/write-adr`, `/handover-note`", "Documented in DEV.md §12"],
     "DEV.md §12"),
    ("v0.0 Foundation", "Set up release-please", "infra", "chore", P1, "S",
     "Changelog and version bumps generated from Conventional Commits.",
     ["release-please workflow + config added", "Release PR opens against main", "DEV.md §10 updated if needed"],
     "DEV.md §10"),
    ("v0.0 Foundation", "Publish docs site to GitHub Pages", "docs", "chore", P0, "S",
     "Docs and devlog are live.",
     ["Pages source set to GitHub Actions", "Docs workflow deploys on merge to main",
      "Site reachable at endodod.github.io/Primordia"],
     "Roadmap Phase 0"),
    ("v0.0 Foundation", "Write devlog #0 (team kickoff)", "docs", "chore", P1, "S",
     "First real devlog post in the team's own words.",
     ["Replaces the placeholder post", "Introduces the team, the idea and the plan, links the roadmap"],
     "DEV.md §17"),
    # ---------------- Phase 1 ----------------
    ("v0.1 First Life", "ADR-0002: numeric strategy (fixed-point vs strict floats)", "engine", "decision", P0, "M",
     "Decide how the engine does math so results are bit-identical on every platform and in WASM.",
     ["Spike both options on a small benchmark", "ADR-0002 accepted by the team",
      "Engine math module skeleton follows the decision"],
     "Roadmap §5.1, §11 (biggest technical risk) - do this first"),
    ("v0.1 First Life", "Engine: world grid, food and energy model", "engine", "feature", P0, "M",
     "A world with tiles that hold food which regrows.",
     ["Grid world with configurable size", "Food per tile with deterministic regrowth",
      "Covered by determinism tests"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Engine: creatures with energy, movement, eating, death", "engine", "feature", P0, "M",
     "Creatures move, eat food, spend energy and die.",
     ["Creature struct with position + energy", "Movement costs energy; eating restores it",
      "Death at zero energy or max age", "Spatial partitioning for neighbor lookups"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Engine: genome v1 and mutation", "engine", "feature", P0, "M",
     "Genes for size, speed, diet, vision, aggression, inherited with mutation.",
     ["Genome type separate from brain", "Mutation rate/strength configurable",
      "Gene values bounded and documented", "Determinism tests updated"],
     "Roadmap Phase 1; DEV.md §13"),
    ("v0.1 First Life", "Engine: reproduction", "engine", "feature", P0, "M",
     "Creatures reproduce when they have enough energy; offspring inherit mutated genomes.",
     ["Energy threshold + cost configurable", "Offspring placed deterministically",
      "Population can grow and crash"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Engine: Brain trait + rule-based brain", "engine", "feature", P0, "M",
     "Behavior behind a `Brain` trait so neural networks can plug in later (Phase 6).",
     ["`Brain` trait: perception in, action out", "Rule-based brain: seek food, flee, wander",
      "Genome does not depend on a brain implementation"],
     "Roadmap Phase 1, Phase 6"),
    ("v0.1 First Life", "Engine: statistics collection per tick", "engine", "feature", P1, "M",
     "Every run records stats that charts and exports use.",
     ["Population, births, deaths, gene means/distributions per N ticks",
      "Stats API usable from desktop", "No effect on determinism"],
     "Roadmap §5.4"),
    ("v0.1 First Life", "Cross-platform determinism CI incl. WASM", "infra", "chore", P0, "M",
     "CI proves the same run gives the same hash on Windows, macOS, Linux and WASM.",
     ["WASM test runner executes the determinism cases", "Golden hashes compared on all 4 targets",
      "Failure message explains how to investigate"],
     "Roadmap §5.1"),
    ("v0.1 First Life", "Performance benchmarks in CI + baseline", "engine", "chore", P0, "M",
     "Measure the engine against the provisional targets.",
     ["Benchmarks for 2k and 10k creatures", "Run in CI with regression alert",
      "Baseline documented; targets confirmed or adjusted in roadmap §5.3"],
     "Roadmap §5.3"),
    ("v0.1 First Life", "Run file format v1 + save/load", "engine", "feature", P0, "M",
     "Runs saved as small versioned files and replayed by re-simulation.",
     ["format_version + engine_version + seed + config + designs + inputs",
      "Save -> load -> replay gives an identical hash", "Fixture file in engine/tests/fixtures/run-files/",
      "`docs/run-format.md` written with example"],
     "Roadmap §5.2"),
    ("v0.1 First Life", "Generate TS types from Rust into packages/types", "desktop", "chore", P1, "S",
     "Types exposed to the frontend are generated, never hand-written.",
     ["Generator chosen (tauri-specta or ts-rs)", "`pnpm types:generate` works",
      "CI fails if generated types are stale"],
     "CLAUDE.md §3"),
    ("v0.1 First Life", "Desktop: procedural creature rendering with PixiJS", "desktop", "feature", P0, "M",
     "Creatures drawn from their genes (size, color by diet, spikes by aggression).",
     ["PixiJS renderer in packages/ui", "Visual mapping documented", "2k creatures at 60 fps on baseline machine"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Desktop: run controls (play, pause, speed, headless)", "desktop", "feature", P0, "S",
     "Control how fast the simulation runs.",
     ["Play/pause", "Speed 1x / 10x / max headless", "Tick counter + state hash visible"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Desktop: basic Creature Designer + release into world", "desktop", "feature", P0, "M",
     "Set genes for a starting creature and release it into the world.",
     ["Gene sliders with preview", "Release N copies at a chosen spot", "Design stored in the run file"],
     "Roadmap Phase 1; team feedback #1"),
    ("v0.1 First Life", "Desktop: population and gene distribution charts", "desktop", "feature", P0, "M",
     "See what evolution is doing.",
     ["Population over time", "Gene distribution histograms", "Charts update live without hurting fps"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Desktop: gene heatmap v1", "desktop", "feature", P1, "M",
     "One gene's distribution across generations at a glance.",
     ["Heatmap: x = time, y = gene value, color = count", "Gene selectable"],
     "Roadmap Phase 1; team feedback #3"),
    ("v0.1 First Life", "Desktop: save and load runs", "desktop", "feature", P0, "S",
     "Use the run file format from the app.",
     ["Save / open dialogs", "Clear error for invalid or newer-version files"],
     "Roadmap Phase 1"),
    ("v0.1 First Life", "Engine docs: how the simulation works (v1)", "docs", "chore", P1, "S",
     "Science background for genome, energy, reproduction.",
     ["Docs page per system", "Linked from intro"],
     "Roadmap Phase 5 docs"),
    # ---------------- Phase 2 ----------------
    ("v0.2 The Lab", "Creature Designer: multiple species, templates, timed release", "desktop", "feature", P0, "M",
     "Design several species and release them at chosen places/times.",
     ["Save designs as templates", "Release scheduled as tick-indexed input", "Baseline stats preview"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "World editor: terrain painting, food sources, world size", "desktop", "feature", P0, "M",
     "Build worlds by hand.",
     ["Paint biomes/barriers", "Place food sources", "World config saved in run file"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Engine: biomes (forest, desert, water, tundra)", "engine", "feature", P0, "M",
     "Each biome changes food yield, temperature and movement cost.",
     ["Biome parameters configurable", "Creatures affected by temperature", "Determinism tests"],
     "Roadmap Phase 2; feedback #3"),
    ("v0.2 The Lab", "Engine: barriers (rivers, mountains)", "engine", "feature", P0, "S",
     "Barriers split populations and enable speciation.",
     ["Impassable or costly tiles", "Pathing respects barriers"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Engine: day/night cycle", "engine", "feature", P1, "S",
     "Vision and activity depend on time of day.",
     ["Cycle length in ticks configurable", "Vision modifier by light level"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Engine: seasons", "engine", "feature", P1, "S",
     "Food growth varies over the year.",
     ["Season length configurable", "Food regrowth multiplied by seasonal factor"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Engine: speciation and automatic species detection", "engine", "feature", P0, "L",
     "Creatures that drift too far apart can't breed; new species are detected and named.",
     ["Genetic distance metric", "Breeding blocked over threshold", "Species clustering + auto names",
      "Split into smaller issues before Ready"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Desktop: species tree (phylogeny) view", "desktop", "feature", P1, "M",
     "See how species branched over time.",
     ["Tree from speciation events", "Click a species to inspect it"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Rules editor + presets", "desktop", "feature", P0, "M",
     "Tune the laws of evolution.",
     ["Mutation, reproduction cost, carrying capacity, predation, aging",
      "Presets: Earth-like, Harsh, Abundant", "Rules saved in run file"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Engine: scheduled events (ice age, drought, meteor, invasive species)", "engine", "feature", P0, "M",
     "Events change the world at chosen ticks.",
     ["Each event type implemented deterministically", "Events stored in run file"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Engine: triggered rules (if X then event)", "engine", "feature", P1, "M",
     "Conditions like 'if population > N, start drought'.",
     ["Condition + action model", "Evaluated at tick boundaries"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Live interventions recorded as tick-indexed inputs", "desktop", "feature", P0, "M",
     "Intervene during a run without breaking replays.",
     ["Interventions saved with tick", "Replay reproduces them exactly", "Determinism test with interventions"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Batch runs: N seeds in parallel with aggregate stats", "desktop", "feature", P0, "M",
     "Run the same experiment across many seeds.",
     ["Parallel across runs only (rayon)", "Mean, spread, confidence intervals", "Progress + cancel"],
     "Roadmap Phase 2, §5.4"),
    ("v0.2 The Lab", "Side-by-side run comparison", "desktop", "feature", P1, "M",
     "Compare two runs' charts directly.",
     ["Pick two runs", "Aligned charts"],
     "Roadmap Phase 2"),
    ("v0.2 The Lab", "Experiment notes (hypothesis / observations)", "desktop", "feature", P1, "S",
     "Keep the science with the run.",
     ["Notes field saved in run file", "Shown in gallery later"],
     "Roadmap §5.4"),
    ("v0.2 The Lab", "Data export (CSV) for charts and raw stats", "desktop", "feature", P0, "S",
     "Everything visible in a chart can be exported.",
     ["CSV per chart + full stats", "Documented columns"],
     "Roadmap §5.4"),
    ("v0.2 The Lab", "Run file format v2 + migration from v1", "engine", "feature", P0, "M",
     "Store biomes, events, interventions, notes.",
     ["format_version 2", "v1 fixture migrates and replays", "run-format doc updated"],
     "Roadmap §5.2"),
    ("v0.2 The Lab", "Phase 2 mid-point scope review", "docs", "decision", P0, "S",
     "Phase 2 is the biggest phase - re-check scope halfway.",
     ["Team review of progress vs plan", "Must/Should list adjusted", "Decide if disease/parasites goes into v1.0"],
     "Roadmap §11, §12"),
    # ---------------- Phase 3 ----------------
    ("v0.3 Local Gallery", "Gallery of local runs (SQLite index, thumbnails, search)", "desktop", "feature", P0, "M",
     "Browse all your runs.",
     ["SQLite index rebuilt from run files", "Thumbnail, tags, notes, filter/search", "100+ runs browse smoothly"],
     "Roadmap Phase 3"),
    ("v0.3 Local Gallery", "Replay viewer with timeline and snapshot seeking", "desktop", "feature", P0, "M",
     "Scrub through any run.",
     ["Cached snapshots for seeking", "Identical to original run"],
     "Roadmap Phase 3"),
    ("v0.3 Local Gallery", "Remix: duplicate a run, change variables, re-run", "desktop", "feature", P0, "S",
     "Fork your own experiments.",
     ["'Derived from' link stored", "Diff of changed settings shown"],
     "Roadmap Phase 3"),
    ("v0.3 Local Gallery", "Auto-generated run summary", "desktop", "feature", P1, "S",
     "One-line summary like '3 species, 1 extinction, predators at gen 340'.",
     ["Summary from stats", "Shown in gallery"],
     "Roadmap Phase 3"),
    ("v0.3 Local Gallery", "Creature inspector: genes, ancestry, cause of death", "desktop", "feature", P1, "M",
     "Click any creature to understand it.",
     ["Genes, parents, descendants count", "Cause of death"],
     "Roadmap Phase 3"),
    ("v0.3 Local Gallery", "Import/export run files", "desktop", "feature", P1, "S",
     "Share runs with friends manually.",
     ["Export to file", "Import validates and opens", "Opens identically on another machine"],
     "Roadmap Phase 3"),
    ("v0.3 Local Gallery", "Cut-line decision: Phase 4 in v1.0 or v1.1", "docs", "decision", P0, "S",
     "Decide whether the leaderboard ships in v1.0.",
     ["Team decision recorded", "Roadmap updated"],
     "Roadmap §6"),
    # ---------------- Phase 4 ----------------
    ("v0.4 Challenges & Leaderboard", "ADR: leaderboard database choice", "web", "decision", P0, "S",
     "Pick a free hosted database for scores.",
     ["Compare free tiers", "ADR accepted", "Vercel project + DB created by owner"],
     "Roadmap §12"),
    ("v0.4 Challenges & Leaderboard", "Challenge format (world, rules, goal, tick limit, scoring)", "engine", "feature", P0, "M",
     "Define what a challenge is.",
     ["Challenge spec pinned to engine_version", "Scoring function in engine", "3 example challenges"],
     "Roadmap Phase 4"),
    ("v0.4 Challenges & Leaderboard", "App identity: display name + generated key pair, signed submissions", "desktop", "feature", P0, "M",
     "Identify submitters without accounts.",
     ["Key pair generated and stored locally", "Run files signed on submit", "Privacy note shown before first submit"],
     "Roadmap §5.5"),
    ("v0.4 Challenges & Leaderboard", "Verification API: re-run submissions in engine.wasm", "web", "feature", P0, "L",
     "The server computes scores itself.",
     ["Validate schema/size/challenge", "Verify signature", "Re-simulate to tick limit, compute score, store",
      "Tampered run rejected", "Verification time benchmarked vs Vercel limits", "Split before Ready"],
     "Roadmap Phase 4; CLAUDE.md §9"),
    ("v0.4 Challenges & Leaderboard", "Leaderboard and challenge pages", "web", "feature", P0, "M",
     "See challenges and rankings on the website.",
     ["Challenge list + detail", "Leaderboard per challenge"],
     "Roadmap Phase 4"),
    ("v0.4 Challenges & Leaderboard", "Challenges in the desktop app + submit flow", "desktop", "feature", P0, "M",
     "Play and submit challenges from the lab.",
     ["Challenge browser in app", "Submit + show server score"],
     "Roadmap Phase 4"),
    ("v0.4 Challenges & Leaderboard", "Moderation: rate limits, name filter, admin hide", "web", "feature", P0, "M",
     "Keep the leaderboard clean.",
     ["Rate limit per key + IP", "Offensive-name filter", "Admin-only hide"],
     "Roadmap §5.5"),
    ("v0.4 Challenges & Leaderboard", "Privacy note (website + app)", "docs", "chore", P0, "S",
     "Explain what we store.",
     ["Lists stored data", "Linked from app and site"],
     "Roadmap §5.5"),
    ("v0.4 Challenges & Leaderboard", "Replay top runs on the website (WASM)", "web", "feature", P2, "M",
     "Watch the best runs in the browser.",
     ["Playback only, no editing", "Uses the same engine.wasm"],
     "Roadmap §6 Could"),
    ("v0.4 Challenges & Leaderboard", "Achievements / experiment milestones", "desktop", "feature", P2, "M",
     "Optional milestones like 'first predator', verified like challenges.",
     ["Team confirms it fits the science tone", "Server-side verification"],
     "Roadmap §6 Could, §12"),
    # ---------------- Phase 5 ----------------
    ("v1.0 Launch", "Installers for Windows, macOS, Linux on GitHub Releases", "infra", "feature", P0, "M",
     "Downloadable desktop app.",
     ["Tauri bundling enabled, real icons", "Release workflow on version tags", "Installs on clean machines"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Tauri auto-updater", "infra", "feature", P1, "M",
     "Users get updates automatically.",
     ["Updater configured with GitHub Releases", "Update tested from previous version"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "ADR: code signing (pay or accept warnings)", "infra", "decision", P0, "S",
     "Decide on Apple notarization / Windows signing.",
     ["ADR accepted", "If unsigned: install guide for each OS"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Onboarding: first-run tutorial experiment", "desktop", "feature", P1, "M",
     "New users understand the lab in minutes.",
     ["Guided first experiment", "Skippable"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Performance and polish pass", "desktop", "chore", P0, "L",
     "Fix rough edges before launch.",
     ["Performance targets met", "UI consistency pass", "Split into concrete issues"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Closed beta with 5-10 outside testers", "docs", "chore", P0, "M",
     "Real feedback before launch.",
     ["Testers recruited", "Feedback collected (Notion Playtest Log)", "P0/P1 findings fixed"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Complete docs: user guide, science background, dev docs", "docs", "chore", P0, "L",
     "Everything documented for launch.",
     ["User guide for every feature", "Science background", "Run format + challenge rules", "Split per section"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Landing page with screenshots and downloads", "web", "feature", P0, "M",
     "A page that sells the project.",
     ["Screenshots/GIFs", "Download links per OS", "Links to docs and devlog"],
     "Roadmap Phase 5"),
    ("v1.0 Launch", "Launch devlog post + v1.0.0 release", "docs", "chore", P0, "S",
     "Ship it.",
     ["All Must items from roadmap §6 shipped", "v1.0.0 tagged", "Launch post published"],
     "Roadmap Phase 5"),
    # ---------------- Phase 6 ----------------
    ("v2.0 Brains", "Neural-network brain implementing the Brain trait", "engine", "feature", P2, "L",
     "Creatures that learn.",
     ["NN brain behind the Brain trait", "Deterministic forward pass", "ENGINE_VERSION bump"],
     "Roadmap Phase 6"),
    ("v2.0 Brains", "Neuroevolution: weights in the genome", "engine", "feature", P2, "L",
     "Network weights inherited and mutated.",
     ["Weights part of genome", "Mutation operators for weights"],
     "Roadmap Phase 6"),
    ("v2.0 Brains", "Brain inspector / visualization", "desktop", "feature", P2, "M",
     "See what a creature's brain does.",
     ["Network graph view", "Live activations"],
     "Roadmap Phase 6"),
    ("v2.0 Brains", "Group behavior (herding, pack hunting, kin help)", "engine", "feature", P2, "L",
     "Emergent social behavior.",
     ["Perception of nearby kin", "Behaviors emerge or are supported by brains"],
     "Roadmap Phase 6, §8"),
    ("v2.0 Brains", "Plant evolution (defenses, arms race)", "engine", "feature", P2, "L",
     "Plants evolve toxins/spikes in response to grazers.",
     ["Plant genome", "Grazer-plant interaction"],
     "Roadmap §8"),
    ("v2.0 Brains", "Disease and parasites", "engine", "feature", P2, "L",
     "Contact spread, co-evolution, population crashes (unless pulled into v1.0).",
     ["Infection model", "Co-evolving pathogen", "Usable as a condition event"],
     "Roadmap §6 Should, §8"),
]


def gh(*args, input_data=None):
    res = subprocess.run(["gh", *args], capture_output=True, text=True, input=input_data)
    if res.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}...: {res.stderr.strip()}")
    return res.stdout


def body_for(goal, criteria, context, size):
    lines = ["## Goal", goal, "", "## Acceptance criteria"]
    lines += [f"- [ ] {c}" for c in criteria]
    lines += ["", "## Context", context, "", f"Size: **{size}**"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="endodod/Primordia")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    repo = args.repo

    if args.dry_run:
        for m, title, area, typ, prio, size, *_ in ISSUES:
            print(f"[{m}] {title}  ({area}, {typ}, {prio}, {size})")
        print(f"{len(ISSUES)} issues")
        return

    for name, (color, desc) in LABELS.items():
        gh("label", "create", name, "--repo", repo, "--color", color, "--description", desc, "--force")
    print(f"labels: {len(LABELS)} ensured")

    existing_ms = {
        m["title"]: m["number"]
        for m in json.loads(gh("api", f"repos/{repo}/milestones?state=all&per_page=100"))
    }
    for title, desc in MILESTONES.items():
        if title not in existing_ms:
            m = json.loads(gh("api", "-X", "POST", f"repos/{repo}/milestones",
                              "-f", f"title={title}", "-f", f"description={desc}"))
            existing_ms[title] = m["number"]
    print(f"milestones: {len(MILESTONES)} ensured")

    existing = set()
    page = 1
    while True:
        batch = json.loads(gh("api", f"repos/{repo}/issues?state=all&per_page=100&page={page}"))
        existing |= {i["title"] for i in batch}
        if len(batch) < 100:
            break
        page += 1

    created = 0
    for m, title, area, typ, prio, size, goal, criteria, context in ISSUES:
        if title in existing:
            continue
        labels = [f"area: {area}", f"type: {typ}", prio, f"size: {size}"]
        if area == "engine" and typ == "feature":
            labels.append("determinism")
        payload = {"title": title, "body": body_for(goal, criteria, context, size),
                   "labels": labels, "milestone": existing_ms[m]}
        gh("api", "-X", "POST", f"repos/{repo}/issues", "--input", "-", input_data=json.dumps(payload))
        created += 1
        print(f"  + {title}")
    print(f"issues: {created} created, {len(ISSUES) - created} already existed")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))

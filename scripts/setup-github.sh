#!/usr/bin/env bash
# One-time GitHub setup for Primordia: repo settings, dev branch, rulesets, labels,
# milestones, Pages and the project board.
#
# Run by a repo admin AFTER the first push to main:
#   gh auth login
#   gh auth refresh -s project,admin:org   # project scope needed for the board
#   ./scripts/setup-github.sh
#
# Safe to re-run: existing rulesets/labels/milestones are updated or skipped.
set -euo pipefail

REPO="${REPO:-endodod/Primordia}"
OWNER="${REPO%%/*}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Repo settings ($REPO)"
gh api -X PATCH "repos/$REPO" \
  -F allow_auto_merge=true \
  -F delete_branch_on_merge=true \
  -F allow_squash_merge=true \
  -F allow_merge_commit=true \
  -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY \
  -F has_issues=true -F has_projects=true -F has_wiki=false >/dev/null

echo "==> dev branch"
if ! gh api "repos/$REPO/branches/dev" >/dev/null 2>&1; then
  MAIN_SHA="$(gh api "repos/$REPO/git/ref/heads/main" -q .object.sha)"
  gh api -X POST "repos/$REPO/git/refs" -f ref=refs/heads/dev -f sha="$MAIN_SHA" >/dev/null
fi
# PRs target dev by default; releases go dev -> main.
gh api -X PATCH "repos/$REPO" -f default_branch=dev >/dev/null

echo "==> Rulesets"
for file in "$ROOT"/.github/rulesets/*.json; do
  name="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["name"])' "$file")"
  id="$(gh api "repos/$REPO/rulesets" -q ".[] | select(.name==\"$name\") | .id" || true)"
  if [[ -n "$id" ]]; then
    gh api -X PUT "repos/$REPO/rulesets/$id" --input "$file" >/dev/null && echo "   updated $name"
  else
    gh api -X POST "repos/$REPO/rulesets" --input "$file" >/dev/null && echo "   created $name"
  fi
done

echo "==> Labels"
label() { gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force >/dev/null; }
label "area: engine"   "8957e5" "Simulation engine"
label "area: desktop"  "1f6feb" "Desktop app"
label "area: web"      "2ea043" "Website / leaderboard"
label "area: docs"     "d29922" "Docs site, ADRs, devlog"
label "area: infra"    "6e7781" "CI, release, repo"
label "type: feature"  "0e8a16" "New functionality"
label "type: bug"      "d73a4a" "Something is broken"
label "type: chore"    "c5def5" "Tooling, refactor, deps"
label "P0"             "b60205" "Must, now"
label "P1"             "fbca04" "Should"
label "P2"             "c2e0c6" "Could"
label "good first issue" "7057ff" "Small, self-contained"
label "determinism"    "e99695" "Affects simulation outcomes"

echo "==> Milestones"
milestone() {
  if ! gh api "repos/$REPO/milestones?state=all" -q ".[].title" | grep -qxF "$1"; then
    gh api -X POST "repos/$REPO/milestones" -f title="$1" -f description="$2" >/dev/null
    echo "   created $1"
  fi
}
milestone "v0.0 Foundation"                 "Phase 0 — repo, CI, a dot moves"
milestone "v0.1 First Life"                 "Phase 1 — creatures evolve deterministically"
milestone "v0.2 The Lab"                    "Phase 2 — designer, biomes, rules, events, batch runs"
milestone "v0.3 Local Gallery"              "Phase 3 — gallery, replays, remix"
milestone "v0.4 Challenges & Leaderboard"   "Phase 4 — verified online leaderboard"
milestone "v1.0 Launch"                     "Phase 5 — installers, docs, beta"
milestone "v2.0 Brains"                     "Phase 6 — neural-network brains"

echo "==> GitHub Pages (Actions)"
gh api -X POST "repos/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 \
  || gh api -X PUT "repos/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 \
  || echo "   (Pages: enable manually under Settings → Pages → Source: GitHub Actions)"

echo "==> Project board"
if ! gh project list --owner "$OWNER" --format json -q '.projects[].title' | grep -qxF "Primordia"; then
  NUMBER="$(gh project create --owner "$OWNER" --title "Primordia" --format json -q .number)"
  gh project link "$NUMBER" --owner "$OWNER" --repo "$REPO" >/dev/null || true
  gh project field-create "$NUMBER" --owner "$OWNER" --name "Area" --data-type SINGLE_SELECT \
    --single-select-options "engine,desktop,web,docs,infra" >/dev/null
  gh project field-create "$NUMBER" --owner "$OWNER" --name "Size" --data-type SINGLE_SELECT \
    --single-select-options "S,M,L" >/dev/null
  gh project field-create "$NUMBER" --owner "$OWNER" --name "Priority" --data-type SINGLE_SELECT \
    --single-select-options "P0,P1,P2" >/dev/null
  echo "   created project #$NUMBER"
fi

cat <<'MANUAL'

Done. A few things the API/CLI can't do — finish them in the browser:
  1. Project → Settings → Status field: options Backlog, Ready, In Progress, In Review, Done
  2. Project → add an "Iteration" field (1–2 week sprints)
  3. Project → Workflows: "Pull request linked" → In Review, "Item closed"/"PR merged" → Done
  4. Settings → Code security: confirm secret scanning + push protection + Dependabot alerts on
  5. Once area owners exist: fill .github/CODEOWNERS and set require_code_owner_review=true
     in .github/rulesets/*.json, then re-run this script
MANUAL

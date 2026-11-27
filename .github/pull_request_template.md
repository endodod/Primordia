## What
<!-- What does this PR change? One issue per PR. -->

Closes #

## Why
<!-- Motivation / context. Link ADRs or docs if relevant. -->

## How to test
<!-- Steps a reviewer can follow. -->

## Screenshots / GIFs
<!-- Required for UI changes. Delete otherwise. -->

## Risk
<!-- What could break? Where should the reviewer look closely? -->
- [ ] Touches `engine/` (determinism) — `ENGINE_VERSION` bumped if outcomes changed
- [ ] Touches the run file format — version bumped + migration + fixture
- [ ] Touches leaderboard verification / stored data

## Checklist
- [ ] Self-reviewed every line of the diff
- [ ] Tests added/updated
- [ ] Docs updated where relevant
- [ ] PR is small enough to review (~400 lines max)

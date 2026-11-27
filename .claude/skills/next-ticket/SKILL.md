---
name: next-ticket
description: Show which Primordia tickets are in progress and which to pick next, and claim one safely so no two agents or people work on the same issue. Use before starting any work, when asked "what should I work on", or to claim/release an issue.
---

# next-ticket

The **issue assignee is the lock.** An assigned issue belongs to that person — never work on it,
never reassign it.

## 1. Look before you pick

```bash
python3 scripts/next-ticket.py
```

Shows **IN PROGRESS** (assigned issues, with open PRs marked) and **NEXT UP** (unassigned,
unblocked, no open PR, current + next milestone, sorted by milestone → priority → size).

- If the developer named an issue, check it appears as available (not assigned to someone else,
  not blocked). If it's taken or blocked, say so and suggest the top NEXT UP items instead.
- If they didn't name one, suggest the top 3 from NEXT UP that fit their area (see `CODEOWNERS` /
  DEV.md §20) and let them choose. Don't pick for them.
- `type: decision` issues are listed separately — humans decide; you may draft an ADR if asked.
- Size L issues are hidden: they must be split into smaller issues first.

## 2. Claim

```bash
python3 scripts/next-ticket.py --claim <N>
```

It refuses if the issue is assigned to someone else, blocked, or already has an open PR, and it
double-checks after assigning (race-safe). On success it comments "🔒 Claimed by @…".
If it fails, **stop** and pick another ticket — never work around it.

Then:
- search Notion **Agent Notes** for earlier notes on the issue
- read the issue + linked docs, propose a plan, and branch as `<type>/<N>-<slug>` from `dev`
- if you have Projects access (local sessions), move the card to **In Progress**

## 3. Release (when stopping without finishing)

```bash
python3 scripts/next-ticket.py --release <N>
```

Write a **Handover** note in Notion Agent Notes first (what's done, what's next, branch name).
Push the branch so the next person can continue.

## Rules

- Max **2** issues assigned per person at a time.
- One issue per branch, one branch per issue.
- Never unassign someone else. If an issue looks abandoned (no activity for 5+ days), tell the
  developer so they can ask in the team chat.

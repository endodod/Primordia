#!/usr/bin/env python3
"""Pick, claim and release tickets so no two people (or agents) work on the same issue.

The issue ASSIGNEE is the lock. It is visible everywhere and works over plain REST, so Claude
Code cloud sessions (which can't read the GitHub Project board) see the same truth as humans.

Usage:
  python3 scripts/next-ticket.py               # what's in progress + what to pick next
  python3 scripts/next-ticket.py --claim 42    # assign yourself, safely
  python3 scripts/next-ticket.py --release 42  # unassign yourself (e.g. when abandoning)

Order of "next": earliest milestone → priority (P0, P1, P2) → size (S, M, L) → issue number.
Only the current milestone and the next one are offered.
Skipped: assigned issues, issues blocked by open issues, issues with an open PR, size L
(must be split first), and `type: decision` issues unless --decisions is given.
"""

import argparse
import json
import re
import subprocess
import sys

PRIORITY = {"P0": 0, "P1": 1, "P2": 2}
SIZE = {"size: S": 0, "size: M": 1, "size: L": 2}


def gh(*args):
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:4])}: {res.stderr.strip()}")
    return res.stdout


def api(path, *extra):
    return json.loads(gh("api", path, *extra) or "null")


def paged(path):
    items, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        batch = api(f"{path}{sep}per_page=100&page={page}")
        items += batch
        if len(batch) < 100:
            return items
        page += 1


def labels(issue):
    return {l["name"] for l in issue["labels"]}


def rank(issue):
    ls = labels(issue)
    milestone = issue["milestone"]["title"] if issue.get("milestone") else "zzz"
    prio = min((PRIORITY[l] for l in ls if l in PRIORITY), default=9)
    size = min((SIZE[l] for l in ls if l in SIZE), default=9)
    return (milestone, prio, size, issue["number"])


def issues_with_open_prs(repo):
    """Issue numbers referenced by open PRs (branch `<type>/<N>-...` or 'Closes/Refs #N')."""
    referenced = set()
    for pr in paged(f"repos/{repo}/pulls?state=open"):
        m = re.match(r"^[a-z]+/(\d+)-", pr["head"]["ref"])
        if m:
            referenced.add(int(m.group(1)))
        for n in re.findall(r"(?:closes|fixes|resolves|refs)\s+#(\d+)", pr.get("body") or "", re.I):
            referenced.add(int(n))
    return referenced


def show(repo, me, include_decisions, limit):
    issues = [i for i in paged(f"repos/{repo}/issues?state=open") if "pull_request" not in i]
    with_pr = issues_with_open_prs(repo)

    in_progress = sorted((i for i in issues if i["assignees"]), key=rank)
    print("IN PROGRESS (assigned — do not touch unless it's yours):")
    for i in in_progress:
        who = ",".join(a["login"] for a in i["assignees"])
        mark = " ← you" if me in who.split(",") else ""
        pr = " [PR open]" if i["number"] in with_pr else ""
        print(f"  #{i['number']:<4} @{who:<14} {i['title']}{pr}{mark}")
    if not in_progress:
        print("  (nothing)")

    def available(i):
        ls = labels(i)
        deps = i.get("issue_dependencies_summary") or {}
        return (not i["assignees"]
                and deps.get("blocked_by", 0) == 0
                and i["number"] not in with_pr
                and "size: L" not in ls
                and (include_decisions or "type: decision" not in ls))

    # Only the current milestone (earliest with open issues) and the one after it.
    open_milestones = sorted({i["milestone"]["title"] for i in issues if i.get("milestone")})
    window = set(open_milestones[:2])
    candidates = sorted((i for i in issues if available(i)
                         and i.get("milestone") and i["milestone"]["title"] in window), key=rank)
    print(f"\nNEXT UP (unassigned, unblocked, milestones: {', '.join(sorted(window))}):")
    for i in candidates[:limit]:
        ls = labels(i)
        tags = " ".join(sorted(l for l in ls if l in PRIORITY or l in SIZE or l.startswith("area:")))
        print(f"  #{i['number']:<4} [{i['milestone']['title'] if i.get('milestone') else '-'}] "
              f"{i['title']}  ({tags})")
    if not candidates:
        print("  (nothing available)")

    decisions = [i for i in issues if not i["assignees"] and "type: decision" in labels(i)
                 and (i.get("issue_dependencies_summary") or {}).get("blocked_by", 0) == 0]
    if decisions and not include_decisions:
        print("\nTEAM DECISIONS WAITING (humans decide; agents may draft an ADR when asked):")
        for i in sorted(decisions, key=rank)[:5]:
            print(f"  #{i['number']:<4} {i['title']}")


def claim(repo, me, number):
    issue = api(f"repos/{repo}/issues/{number}")
    if issue["state"] != "open":
        sys.exit(f"#{number} is closed.")
    owners = [a["login"] for a in issue["assignees"]]
    if owners and owners != [me]:
        sys.exit(f"#{number} is already claimed by @{', @'.join(owners)}. Pick another ticket.")
    blocked = (issue.get("issue_dependencies_summary") or {}).get("blocked_by", 0)
    if blocked:
        sys.exit(f"#{number} is blocked by {blocked} open issue(s). Pick another ticket.")
    if number in issues_with_open_prs(repo):
        sys.exit(f"#{number} already has an open PR. Pick another ticket.")

    gh("api", "-X", "POST", f"repos/{repo}/issues/{number}/assignees", "-f", f"assignees[]={me}",
       "--silent")
    owners = [a["login"] for a in api(f"repos/{repo}/issues/{number}")["assignees"]]
    if owners != [me]:  # someone claimed it at the same moment
        gh("api", "-X", "DELETE", f"repos/{repo}/issues/{number}/assignees",
           "-f", f"assignees[]={me}", "--silent")
        sys.exit(f"#{number} was claimed by someone else just now. Pick another ticket.")

    gh("api", "-X", "POST", f"repos/{repo}/issues/{number}/comments",
       "-f", f"body=🔒 Claimed by @{me}. Work starts on a `<type>/{number}-...` branch.", "--silent")
    slug = re.sub(r"[^a-z0-9]+", "-", issue["title"].lower()).strip("-")[:40].rstrip("-")
    print(f"Claimed #{number}: {issue['title']}")
    print(f"Suggested branch: feat/{number}-{slug}  (use fix/, chore/, docs/ … as fitting)")


def release(repo, me, number):
    gh("api", "-X", "DELETE", f"repos/{repo}/issues/{number}/assignees", "-f", f"assignees[]={me}",
       "--silent")
    gh("api", "-X", "POST", f"repos/{repo}/issues/{number}/comments",
       "-f", f"body=🔓 Released by @{me}. See the handover note in Notion if any.", "--silent")
    print(f"Released #{number}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default="endodod/Primordia")
    ap.add_argument("--claim", type=int, metavar="N")
    ap.add_argument("--release", type=int, metavar="N")
    ap.add_argument("--decisions", action="store_true", help="include type: decision issues")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    me = gh("api", "user", "-q", ".login").strip()
    if args.claim:
        claim(args.repo, me, args.claim)
    elif args.release:
        release(args.repo, me, args.release)
    else:
        show(args.repo, me, args.decisions, args.limit)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
